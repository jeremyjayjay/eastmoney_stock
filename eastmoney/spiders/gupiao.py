# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
import re
import requests
from eastmoney.items import EastmoneyItem


class GupiaoSpider(scrapy.Spider):
    name = 'gupiao'
    allowed_domains = ['dfcfw.com']
    # 通过抓包工具Fiddler分析请求头信息得到的起始url,page=1
    start_urls = ['http://quote.eastmoney.com/centerv2/hsgg/xg']

    def parse(self, response):
        # 获取第一页response
        response = requests.get('http://nufm.dfcfw.com/EM_Finance2014NumericApplication/JS.aspx?type=CT&cmd=C.BK05011&sty=FCOIATA&sortType=(ChangePercent)&sortRule=1&page=1&pageSize=20&js=var%20dfFHBxOP={rank:[(x)],pages:(pc),total:(tot)}&token=7bc05d0d4c3c22ef9fca8c2a912d779c&jsName=quote_123&_g=0.628606915911589&_=1523274953883')
        # 正则匹配得到所有页数
        total = re.findall('total:(.*?)}',response.text)[0]
        page = int(total)//20 + 1
        # 循环遍历各页
        for i in range(1,page+1):
            # 拼接所有页的url,总计新股17页
            url = 'http://nufm.dfcfw.com/EM_Finance2014NumericApplication/JS.aspx?type=CT&cmd=C.BK05011&sty=FCOIATA&sortType=(ChangePercent)&sortRule=1&page='+str(i)+'&pageSize=20&js=var%20dfFHBxOP={rank:[(x)],pages:(pc),total:(tot)}&token=7bc05d0d4c3c22ef9fca8c2a912d779c&jsName=quote_123&_g=0.628606915911589&_=1523274953883'
            # 生成request对象,回调函数传给函数parse_num
            request = Request(url, callback=self.parse_num)
            # request传递给框架的downloader处理,生成response给下一个函数
            yield request

    def parse_num(self, response):
        # 取得response中的text文本
        text = response.text
        # 利用爆炸和替换取得股票列表
        stock_list = eval(text.split('=')[1].split(':')[1].replace(',pages',''))
        # 遍历取得股票列表中个股所需信息
        for stock in stock_list:
            stock_msg_list = stock.split(',')
            # 股票代码
            stock_num = stock_msg_list[1]
            # 股票名称
            stock_name = stock_msg_list[2]
            # 股票最新价
            stock_price = stock_msg_list[3]
            # 股票涨跌幅
            stock_change_range = stock_msg_list[5].replace('%','')
            # 股票涨跌额
            stock_change_price = stock_msg_list[4]
            # 将股票代码'30'开头的创业板股票剔除
            if not stock_num.startswith('30'):
                print("代码:%s 名称:%s 现价:%s 涨跌幅:%s 涨跌额:%s"%(stock_num,stock_name,stock_price,stock_change_range,stock_change_price))
                # 生成item对象
                item = EastmoneyItem()
                item['stock_num'] = stock_num
                item['stock_name'] = stock_name
                item['stock_price'] = stock_price
                item['stock_change_range'] = stock_change_range
                item['stock_change_price'] = stock_change_price
                yield item
                self.logger.info('ok')
        print('$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$')




'''
总结:
# 此项目最主要的难点是Fiddler抓包取得异步加载的多页股票数据,抓到包后分析请求头得到json数据的url,分析得到page规律
# 需要获取其他的字段的另外添加即可,此处只演示至此
'''