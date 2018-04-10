from scrapy import cmdline
import time


# 实时监控
while True:
    now_tamp = int(time.time())
    # 指定需要监控的时间点
    dt = "2018-04-10 20:29:00"
    # 转换成时间数组
    time_array = time.strptime(dt, "%Y-%m-%d %H:%M:%S")
    # 转换成时间戳
    times_tamp = int(time.mktime(time_array))
    # 判断当前时间是否已经到了指定时间点
    if now_tamp == times_tamp:
        print('当前时间是:%s'%str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))))
        # 执行爬虫程序
        cmdline.execute("scrapy crawl gupiao".split())
        break