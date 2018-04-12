# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class EastmoneyItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    stock_num = scrapy.Field()
    stock_name = scrapy.Field()
    stock_price = scrapy.Field()
    stock_change_range = scrapy.Field()
    stock_change_price = scrapy.Field()

