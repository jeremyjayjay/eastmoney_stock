## 项目简介
    基于python3,实现爬取东方财富网泸深新股(除了创业板30开头的股票)实时股票信息的功能
## 环境要求:
    环境及模块:python3+scrapy框架+Fiddler抓包工具
## 项目主要方法:
    东方财富网打开新股列表后,可以发现下一页加载的方式为异步加载的方式, 
    不能直接根据url获取所有页面的股票信息,所以需要Fiddler进行抓包, 
    抓包取得每页股票信息列表的json数据,根据请求头的url分析其所有页面json对应url 
    的规律,使用scrapy进行爬取
## 运行说明： 
    1.run.py文件里启动程序，去掉While True 循环直接运行可以实时运行 
    
    2.在run.py文件While True循环里设置target_time，可实现程序在该指定时间点爬取信息
## 入库说明：
    将项目获取的数据按字段存入mysql数据库中，数据库版本：Mysql 5.7，使用模块：pymsql 
    
    我在项目数据库里的初始命名 
    
    数据库名为：eastmoney
    
    表名为：gupiao 
    
    各字段名依次为：stock_num/stock_name/stock_price/stock_change_range/stock_change_price 
