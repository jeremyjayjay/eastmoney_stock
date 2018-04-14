from celery import Celery
from celery.schedules import crontab
from scrapy import cmdline
from eastmoney.pipelines import EastmonyMysqlPipeline

# 生成Celery对象,设置broker存储地址为redis://localhost:6379/1
app = Celery('tasks', broker='redis://localhost:6379/1')

@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # 让程序每隔一段时间执行一次,这里设置为15s
    sender.add_periodic_task(15, crawl.s())

    # 让程序每隔一段时间执行一次,并且加上超时跳过功能,此处expires=20,超过20秒跳过此任务
    # sender.add_periodic_task(15.0, crawl.s(), expires=20)

    # 设置为在某个时间点执行,以下为每周一的7:30am执行
    # sender.add_periodic_task(crontab(hour=7, minute=30, day_of_week=1), crawl.s(),)

# 用celery的task函数装饰crawl爬虫启动函数
@app.task
def crawl():
    EastmonyMysqlPipeline().truncate_table()
    cmdline.execute("scrapy crawl gupiao".split())
