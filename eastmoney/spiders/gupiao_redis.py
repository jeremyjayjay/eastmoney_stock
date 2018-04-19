# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
from eastmoney.items import EastmoneyItem
from redis import Redis


class GupiaoSpider(scrapy.Spider):
    name = 'gupiao_redis'
    allowed_domains = ['dfcfw.com']
    # 通过抓包工具Fiddler分析请求头信息得到的起始url,page=1
    start_urls = ['http://quote.eastmoney.com/centerv2/hsgg/xg']

    def parse(self, response):
        url_list = []
        r = Redis(host='127.0.0.1', port=6379)

        # 注意:这里的redis_total参数是当前运行的机器每次循环时从redis获取的url数量,
        # 建议设成page/机器(运行)个数,取整,本次示例设为每次拿取17页
        redis_total = 17

        # 循环从redis拿取待爬url放入列表中
        for i in range(redis_total):
            if r.scard('myspider:start_urls'):
                u = r.spop('myspider:start_urls').decode(encoding="utf-8")
                url_list.append(u)
        for url in url_list:
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
# 此gupiao_redis.py爬虫在gupiao.py功能基础下增加了利用redis分配url以实现分布式爬虫的功能
'''