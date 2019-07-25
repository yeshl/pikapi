import logging.handlers
import os
import sys
import concurrent_log_handler

_formatter = logging.Formatter(
   # fmt='[%(asctime)s] %(name)s <%(processName)s>%(threadName)s - [%(filename)s:%(lineno)s]%(levelname)5s : %(message)s',
   fmt='[%(asctime)s] <%(processName)s>%(threadName)s - [%(filename)s:%(lineno)s]%(levelname)5s : %(message)s',
   # datefmt="%Y-%m-%d %H:%M:%S"
)
_ch = logging.StreamHandler(sys.stdout)
_ch.setLevel(logging.DEBUG)
_ch.setFormatter(_formatter)

#开发时日志目录
logdir = os.path.dirname(os.path.abspath(__file__))+'/log'
#发布后日志目录请自行修改
# logdir = '.'
logfile = '{}/{}.log'.format(logdir, __package__)
# _fh = logging.handlers.RotatingFileHandler(logfile, "a", maxBytes=1000000, backupCount=5)
# 多进程日志
_fh = concurrent_log_handler.ConcurrentRotatingFileHandler(logfile, "a", maxBytes=1000000, backupCount=5)
_fh.setLevel(logging.DEBUG)
_fh.setFormatter(_formatter)

logger = logging.getLogger(__package__)  # 设置顶级包的logger
# logger = logging.getLogger() #无参数是设置root根logger
logger.setLevel(logging.DEBUG)
logger.addHandler(_ch)
logger.addHandler(_fh)
logger.debug('applog.py loaded logfile:%s' % logfile)
