import multiprocessing
import os

bind = "0.0.0.0:8080"
workers = int(os.getenv('GUNICORN_WORKER_COUNT', multiprocessing.cpu_count() * 2 + 1))
timeout = int(os.getenv('GUNICORN_TIMEOUT', '30'))
accesslog = '-'
access_log_format = os.getenv('GUNICORN_ACCESS_LOG_FORMAT', '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(L)ss %(b)s "%(f)s" "%(a)s"')
errorlog = '-'
pidfile = os.getenv('GUNICORN_PIDFILE', '/var/run/gunicorn.pid')
