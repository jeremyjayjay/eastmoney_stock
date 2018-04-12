from scrapy import cmdline
import time


# 立即执行爬虫
def now_play():
    cmdline.execute("scrapy crawl gupiao".split())

# 指定时间执行爬虫
def set_time(the_time):
    # 实时监控
    while True:
        # 当前时间戳
        now_tamp = int(time.time())
        # 指定需要监控的时间点
        target_time = str(the_time)
        # 转换成时间数组
        time_array = time.strptime(target_time,"%Y-%m-%d %H:%M:%S")
        # 转换成时间戳
        times_tamp = int(time.mktime(time_array))
        # 判断当前时间是否已经到了指定时间点
        if now_tamp == times_tamp:
            print('当前时间是:%s'%str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))))
            # 执行爬虫程序
            cmdline.execute("scrapy crawl gupiao".split())
            break

if __name__ == '__main__':
    # 输入要开始爬取的时间点,精确到秒
    # set_time('2018-04-12 16:14:00')
    now_play()