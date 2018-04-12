# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymysql
from scrapy.utils.project import get_project_settings


class EastmonyMysqlPipeline(object):

    def __init__(self):
        settings = get_project_settings()
        self.database = settings['DATABASE']
        self.connect()

    def connect(self):
        # 连接数据库
        self.conn = pymysql.connect(
            host = self.database['host'],
            port = self.database['port'],
            user = self.database['user'],
            password = self.database['password'],
            db = self.database['db'],
            charset = self.database['charset'],
        )
        self.cursor = self.conn.cursor()

    def process_item(self, item, spider):
        sql = 'insert into gupiao(stock_num,stock_name,stock_price,stock_change_range,stock_change_price) values(%d,"%s",%f,%f,%f)' \
              % (int(item["stock_num"]),item["stock_name"],float(item["stock_price"]),float(item["stock_change_range"]),float(item["stock_change_price"]))
        self.cursor.execute(sql)
        self.conn.commit()
        return item

    def close_spider(self,spider):
        self.cursor.close()
        self.conn.close()

    # 清空表格数据,并且主键初始化为1
    def truncate_table(self):
        sq1 = 'TRUNCATE TABLE gupiao'
        self.cursor.execute(sq1)
        self.close_spider(self)


