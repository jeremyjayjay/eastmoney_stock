import re
from celery import Celery
from celery.schedules import crontab
from scrapy import cmdline
from eastmoney.pipelines import EastmonyMysqlPipeline
from redis import Redis
import requests


# 生成Celery对象,设置broker存储地址为redis://localhost:6379/1
app = Celery('tasks', broker='redis://localhost:6379/1')

r = Redis(host='127.0.0.1', port=6379)


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):

    # Master爬虫启动
    # 让Master的程序每隔一段时间执行一次,这里设置为5s
    sender.add_periodic_task(5, crawl.s())

    # slave 爬虫启动
    # sender.add_periodic_task(5, slave_crawl.s())

    # 让程序每隔一段时间执行一次,并且加上超时跳过功能,此处expires=20,超过20秒跳过此任务
    # sender.add_periodic_task(15.0, crawl.s(), expires=20)

    # Master 启动初始获取总记录数,Slave需要关闭
    # 设置为在某个时间点执行,以下为每周一到周五早上9点25分集合竞价结束时运行收集数据,时区相差8小时
    sender.add_periodic_task(crontab(hour='10', minute='55',day_of_week='1,2,3,4,5'), get_total.s(),)

# 往redis中以set格式塞入所有待爬取的url
def set_url():
    # 获取第一页response
    response = requests.get(
        'http://nufm.dfcfw.com/EM_Finance2014NumericApplication/JS.aspx?type=CT&cmd=C.BK05011&sty=FCOIATA&sortType=(ChangePercent)&sortRule=1&page=1&pageSize=20&js=var%20dfFHBxOP={rank:[(x)],pages:(pc),total:(tot)}&token=7bc05d0d4c3c22ef9fca8c2a912d779c&jsName=quote_123&_g=0.628606915911589&_=1523274953883')
    # 正则匹配得到所有页数
    total = re.findall('total:(.*?)}', response.text)[0]
    page = int(total) // 20 + 1
    # 循环遍历各页url并写进redis
    for i in range(1, page + 1):
        url = 'http://nufm.dfcfw.com/EM_Finance2014NumericApplication/JS.aspx?type=CT&cmd=C.BK05011&sty=FCOIATA&sortType=(ChangePercent)&sortRule=1&page=' + str(
            i) + '&pageSize=20&js=var%20dfFHBxOP={rank:[(x)],pages:(pc),total:(tot)}&token=7bc05d0d4c3c22ef9fca8c2a912d779c&jsName=quote_123&_g=0.628606915911589&_=1523274953883'
        r.sadd('myspider:start_urls', url)

# 获取mysql数据库当天开盘时可以正常交易的新股股票总记录数
@app.task
def get_total():
    p = EastmonyMysqlPipeline()
    # 将结果写进文件
    f = open('./sum.txt', 'w', encoding='utf-8')
    try:
        cmdline.execute("scrapy crawl gupiao".split())
    except:
        pass
    f.write(str(p.count_num()))
    # 格式化redis数据库,防止下次手动启动程序时celery的worker自动爬取之前的url
    r.flushall()

# 用celery的task函数装饰crawl爬虫启动函数,Master版
@app.task
def crawl():
    sum1 = None
    try:
        # 从文件中读取总记录数
        file = open('sum.txt')
        sum1 = file.read()
        print(sum1)
        file.close()
    except:
        pass
    if sum1:
        # 判断redis中是否有url
        if r.scard('myspider:start_urls')==0:
            # 没有则写入url
            set_url()
        # 存在url
        else:
            t =EastmonyMysqlPipeline()
            # 判断数据库已经写入的数据是否已经是全部
            if t.count_num() >= int(sum1):
                # 如果已经存满,则清空循环存放下一次的
                t.truncate_table()
                # 开始爬取
                cmdline.execute("scrapy crawl gupiao_redis".split())
            else:
                cmdline.execute("scrapy crawl gupiao_redis".split())

# slave 版执行爬取并入库
@app.task
def slave_crawl():
    cmdline.execute("scrapy crawl gupiao_redis".split())

'''
# 注: 1. 先启动Master版,至少半分钟后再启动slave版,Master需启动两个定时器(见上述)
      2. 爬取时先启动celery的worker监听任务消息列表: 终端输入celery -A tasks -l INFO worker
      3. 接着启动定时器往队列写入任务: 开启另一个终端celery -A tasks -l INFO beat  即可运行程序
      4. 注意不能在一个url仍在爬取时突然切断,易引发celery任务写入和mysql存库冲突,若有发生冲突,重启系统并清空一次redis即可重新爬取
'''