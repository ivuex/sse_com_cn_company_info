# -*- coding:utf-8 -*-

import json
import random
import pymongo
# import asyncio

from prettytable import PrettyTable
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

header = {}
header['referer'] = 'http://listxbrl.sse.com.cn/companyInfo/toCompanyInfo.do?stock_id=600000&report_period_id=5000'

class CompanyInfoFetcher():
    def __init__(self,timeout=20,options=None):
        self.timeout = timeout
        self.options = options
        self.browser = webdriver.Chrome(options=self.options)
        # 设置超时对象
        self.wait = WebDriverWait(self.browser, self.timeout)
        header['user-agent'] = self.get_user_agent()
        # 数据库初始化
        client = pymongo.MongoClient('45.249.94.149')
        db = client['shangjiaosuo_sse_com_cn']
        self.collection = db['company_years_meta_info']

    def access_pages(self):
        print('45-45')
        stock_codes = self.get_stock_codes()
        for stock_code in stock_codes:
            self.browser.get('http://listxbrl.sse.com.cn/companyInfo/toCompanyInfo.do?stock_id={0:s}&report_period_id=5000'.format(stock_code))
            # 等待页面表格数据元素加载出来
            self.wait.until(
                EC.presence_of_element_located((By.XPATH, '/html[1]/body[1]/div[5]/div[1]/div[1]/div[1]/div[1]/div[2]/div[2]/table[1]/tbody[1]/tr[1]/td[2]/div[1]/div[1]')))
            self.parse_page()

    def parse_page(self):
        '''
        在浏览器中执行以下js代码可以获得 metas 数组
        [].slice.call(document.querySelectorAll('body.easyui-layout.layout:nth-child(2) div.panel.layout-panel.layout-panel-center:nth-child(8) div.panel-body.panel-body-noheader.panel-body-noborder.layout-body.panel-noscroll div.panel.datagrid.propertygrid:nth-child(1) div.datagrid-wrap.panel-body.panel-body-noheader div.datagrid-view div.datagrid-view2:nth-child(3) div.datagrid-body table.datagrid-btable tbody:nth-child(1) tr.datagrid-row td:nth-child(1) > div.datagrid-cell.datagrid-cell-c6-name')).map(item => item.innerText)
        -----------------------------------------
        # 在浏览器中执行以下js代码可以获得 years 数组
        [].slice.call(document.querySelectorAll(
            'body.easyui-layout.layout:nth-child(2) div.panel.layout-panel.layout-panel-center:nth-child(8) div.panel-body.panel-body-noheader.panel-body-noborder.layout-body.panel-noscroll div.panel.datagrid.propertygrid:nth-child(1) div.datagrid-wrap.panel-body.panel-body-noheader div.datagrid-view div.datagrid-view2:nth-child(3) div.datagrid-header div.datagrid-header-inner table.datagrid-htable tbody:nth-child(1) tr.datagrid-header-row td div.datagrid-cell > span:nth-child(1)')).map(
            item => item.innerText).slice(1)
        '''
        metas = ["公司法定中文名称", "公司法定代表人", "公司注册地址", "公司办公地址邮政编码", "公司国际互联网网址", "公司董事会秘书姓名", "公司董事会秘书电话", "公司董事会秘书电子信箱", "报告期末股东总数", "每10股送红股数", "每10股派息数（含税）", "每10股转增数", "本期营业收入(元)", "本期营业利润(元)", "利润总额(元)", "归属于上市公司股东的净利润(元)", "归属于上市公司股东的扣除非经常性损益的净利润(元)", "经营活动产生的现金流量净额(元)", "总资产(元)", "所有者权益（或股东权益）(元)", "基本每股收益(元/股)", "稀释每股收益(元/股)", "扣除非经常性损益后的基本每股收益(元/股)", "全面摊薄净资产收益率（%）", "加权平均净资产收益率（%）", "扣除非经常性损益后全面摊薄净资产收益率（%）", "扣除非经常性损益后的加权平均净资产收益率（%）", "每股经营活动产生的现金流量净额(元/股)", "归属于上市公司股东的每股净资产（元/股）"]
        years = ["2017", "2016", "2015", "2014", "2013"]

        table = PrettyTable(['指标/年份'] + years)

        company = {}
        for i, meta in enumerate(metas):
            row_num = int(i) + 1
            for j, year in enumerate(years):
                col_num = int(j) + 1
                value = self.browser.find_element_by_xpath('/html[1]/body[1]/div[5]/div[1]/div[1]/div[1]/div[1]/div[2]/div[2]/table[1]/tbody[1]/tr[{0:d}]/td[{1:d}]/div[1]'.format(row_num, col_num)).text
                if not meta in company:
                    company[meta] = {}
                company[meta][year] = value
            table.add_row([meta] + list(company[meta].values()))
        self.collection.insert_one(company)
        print(table)
        print('{0:<50}{1:10}{0:>50}'.format('*' * 30, '分割线'))

    def get_stock_codes(self):
        try:
            with open('/Users/apple/PycharmProjects/sse_com_cn_company_info/sse_com_cn_company_info/shangjiaoshuo_stock_codes.list.json', 'r') as f:
                stock_codes = json.loads(f.read())
                # print(self.stock_codes)
            f.close()
            return  stock_codes
        except Exception:
            raise(Exception)


    def get_user_agent(self):
        return random.choice([
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36",
            "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
            "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; Acoo Browser; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.0.04506)",
            "Mozilla/4.0 (compatible; MSIE 7.0; AOL 9.5; AOLBuild 4337.35; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
            "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)",
            "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)",
            "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)",
            "Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 3.0.04506.30)",
            "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) Arora/0.3 (Change: 287 c9dfb30)",
            "Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6",
            "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1",
            "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0",
            "Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Kazehakase/0.4.5",
            "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko Fedora/1.9.0.8-1.fc10 Kazehakase/0.5.6",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20",
            "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; fr) Presto/2.9.168 Version/11.52",
            "Mozilla/5.0 (Windows; U; Windows NT 5.2) Gecko/2008070208 Firefox/3.0.1",
            "Mozilla/5.0 (Windows; U; Windows NT 5.1) Gecko/20070309 Firefox/2.0.0.3",
            "Mozilla/5.0 (Windows; U; Windows NT 5.1) Gecko/20070803 Firefox/1.5.0.12",
            "Opera/9.27 (Windows NT 5.2; U; zh-cn)",
            "Mozilla/5.0 (Windows; U; Windows NT 5.2) AppleWebKit/525.13 (KHTML, like Gecko) Version/3.1 Safari/525.13",
            "Mozilla/5.0 (iPhone; U; CPU like Mac OS X) AppleWebKit/420.1 (KHTML, like Gecko) Version/3.0 Mobile/4A93 ",
            "Mozilla/5.0 (Windows; U; Windows NT 5.2) AppleWebKit/525.13 (KHTML, like Gecko) Chrome/0.2.149.27 ",
            "Mozilla/5.0 (Linux; U; Android 3.2; ja-jp; F-01D Build/F0001) AppleWebKit/534.13 (KHTML, like Gecko) Version/4.0 Safari/534.13 ",
            "Mozilla/5.0 (iPhone; U; CPU iPhone OS 4_1 like Mac OS X; ja-jp) AppleWebKit/532.9 (KHTML, like Gecko) Version/4.0.5 Mobile/8B117 Safari/6531.22.7",
            "Mozilla/5.0 (iPhone; U; CPU iPhone OS 4_2_1 like Mac OS X; da-dk) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8C148 Safari/6533.18.5 ",
            "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_5_6; en-US) AppleWebKit/530.9 (KHTML, like Gecko) Chrome/ Safari/530.9 ",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
            "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; 360SE)",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.11 (KHTML, like Gecko) Ubuntu/11.10 Chromium/27.0.1453.93 Chrome/27.0.1453.93 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36",
            "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.94 Safari/537.36",
            "Mozilla/5.0 (Linux; Android 5.1.1; Nexus 6 Build/LYZ28E) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Mobile Safari/537.36"
        ])

if __name__ == '__main__':
    fetcher = CompanyInfoFetcher()
    fetcher.access_pages()

