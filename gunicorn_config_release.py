# config.py
import os

import multiprocessing

# debug = True
loglevel = 'debug'
bind = "0.0.0.0:8080"
pidfile = "/home/pingpongus/pythonserver/virtualenv/pingpongus/app/log/gunicorn.pid"
accesslog = "/home/pingpongus/pythonserver/virtualenv/pingpongus/app/log/access.log"
errorlog = "/home/pingpongus/pythonserver/virtualenv/pingpongus/app/log/debug.log"
daemon = True

# 启动的进程数
workers = multiprocessing.cpu_count()
x_forwarded_for_header = 'X-FORWARDED-FOR'
