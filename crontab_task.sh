#! /bin/bash

# 定时任务
# 25 11 * * * (/bin/sh /my/python/scrapy/project/proxyip/crontab_task.sh)
# 进入proxyip项目目录
cd /my/python/scrapy/project/proxyip

# 检测数据库中所有的代理ip是否有效
nohup python proxyip/crontab_testip.py > crontab_testip.log 2>&1 &

# 启动爬虫，并指定日志文件，其中nohup....&表示可以在后台执行，不会因为关闭终端而导致程序执行中断。
nohup scrapy crawl ipspider > proxyip.log 2>&1 &