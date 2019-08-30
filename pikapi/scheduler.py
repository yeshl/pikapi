import queue
import threading
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from logging.handlers import RotatingFileHandler
from threading import Thread

from pikapi.config import get_config
from pikapi.database import ProxyIP, ProxyWebSite, _db
from pikapi.spiders import *
from pikapi.squid import Squid
from pikapi.validators.validate_manager import ValidateManager

logger = logging.getLogger(__name__)


class BoundedThreadPoolExecutor(ThreadPoolExecutor):
    def __init__(self, max_workers=None, thread_name_prefix=''):
        super().__init__(max_workers, thread_name_prefix)
        self._work_queue = queue.Queue(max_workers)


class TimerJob:
    def __init__(self, interval, function, *args, **kwargs):
        self._lock = threading.Lock()
        self._timer = None
        self.function = function
        self.interval = interval
        self.args = args
        self.kwargs = kwargs
        self._stopped = True
        self.start()

    def start(self, from_run=False):
        self._lock.acquire()
        if from_run or self._stopped:
            self._stopped = False
            self._timer = threading.Timer(self.interval, self._run)
            self._timer.setDaemon(True)
            self._timer.start()
            self._lock.release()

    def _run(self):
        self.start(from_run=True)
        self.function(*self.args, **self.kwargs)

    def stop(self):
        self._lock.acquire()
        self._stopped = True
        self._timer.cancel()
        self._lock.release()


def callback(future):
    try:
        rst = future.result()
    except Exception as e:
        logger.info("callback error %s", e, exc_info=True)


class Scheduler(object):
    # spider_queue = queue.Queue(32)
    validator_queue = queue.Queue(2048)
    thread_pool = BoundedThreadPoolExecutor(max_workers=256)

    def __init__(self):
        self.last_crawl_time = None
        self._stop = False

    def sche_validate_from_db(self):
        try:
            i = 0
            with _db.connection_context():
                proxies = ProxyIP.select().where((ProxyIP.updated_at < datetime.now() - timedelta(minutes=5))
                                                 & (ProxyIP.https_weight + ProxyIP.http_weight > 0))
                for p in proxies.iterator():
                    Scheduler.validator_queue.put(p)
                    i += 1
            logger.info('proxy from db :{}'.format(i))
        except Exception as e:
            logger.error("error:%s", str(e), exc_info=True)

    def crawl_callback(self, future):
        try:
            provider, exc = future.result()
            proxies = list(set(provider.proxies))
            pw = ProxyWebSite(site_name=provider.name)
            if exc is None:
                pw.stats = 'OK'
            else:
                pw.stats = exc.__class__.__name__
                logger.debug("{} crawl error:{}".format(provider.name, exc))

            pw.proxy_count = len(proxies)
            logger.info("{} crawl proxies:{}".format(provider.name, pw.proxy_count))
            for p in proxies:
                self.validator_queue.put(ProxyIP(ip=p[0], port=p[1]))
            logger.info("{} proxies enqueue:{}".format(provider.name, pw.proxy_count))
            logger.info("{} proxies save to db:{}".format(provider.name, pw.proxy_count))
            pw.merge()
            logger.info("{} crawl END".format(provider.name, pw.proxy_count))
        except Exception as e:
            pw.stats = e.__class__.__name__
            logger.debug("{} crawl callback error:{}".format(provider.name, exc))

    def crawls(self):
        while not self._stop:
            try:
                self.last_crawl_time = datetime.now()
                for p in all_providers:
                    future = self.thread_pool.submit(p().crawl)
                    future.add_done_callback(self.crawl_callback)
                time.sleep(60*10)
            except (KeyboardInterrupt, SystemExit):
                logger.info('KeyboardInterrupt terminates crawls()')
                break;

    def sche(self):
        logger.info('schedule validate_from_db ')
        TimerJob(60, self.sche_validate_from_db)
        if get_config('squid'):
            logger.info('schedule squid ')
            sq = Squid()
            TimerJob(60 * 3, sq.reconfigure)

    @staticmethod
    def validate_proxy_ip(p):
        if ValidateManager.should_validate(p):
            v = ValidateManager(p)
            try:
                v.validate()
            except (KeyboardInterrupt, SystemExit):
                logger.info('KeyboardInterrupt terminates validate_proxy_ip()')
        else:
            logger.debug('skip validate {} '.format(p))
        return 0

    def validate(self):
        while not self._stop:
            try:
                proxy: ProxyIP = self.validator_queue.get()
                if not get_config('no_validate'):
                    # logger.debug("submit validate :%s" % proxy.ip)
                    task = self.thread_pool.submit(self.validate_proxy_ip, p=proxy)
                else:
                    logger.debug("no_validate :%s" % proxy.ip)
            except (KeyboardInterrupt, SystemExit):
                break
            except Exception as ex:
                logger.error("error:%s", str(ex), exc_info=True)

    def start(self):
        future = self.thread_pool.submit(self.crawls)
        future = self.thread_pool.submit(self.validate)
        self.sche()

    def join(self):
        while True:
            logger.info('<<<last_crawl_time:{} validator_queue:{}>>>'
                        .format(self.last_crawl_time, self.validator_queue.qsize()))
            time.sleep(4)

    def stop(self):
        self._stop = True
        self.validator_queue.close()
        self.thread_pool.shutdown(wait=False)
