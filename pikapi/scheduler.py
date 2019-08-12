import multiprocessing
import queue
import threading
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from logging.handlers import RotatingFileHandler
from multiprocessing import Queue, Process
from threading import Thread

from pikapi.config import get_config
from pikapi.database import ProxyIP, ProxyWebSite
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


def crawl_callback(future):
    provider, validator_queue, exc = future.result()
    proxies = list(set(provider.proxies))
    pw: ProxyWebSite = ProxyWebSite(site_name=provider.name)
    if exc is None:
        pw.stats = 'OK'
    else:
        pw.stats = exc.__class__.__name__
        logger.debug("{} crawl error:{}".format(provider.name, exc))

    pw.proxy_count = len(proxies)
    logger.info("{} crawl proxies:{}".format(provider.name, pw.proxy_count))
    for p in proxies:
        validator_queue.put(ProxyIP(ip=p[0], port=p[1]))
    pw.merge()
    logger.info("{} crawl END".format(provider.name, pw.proxy_count))

def crawl_ips(spider_queue, validator_queue):
    # if sys.platform.startswith('linux'):
    pn = multiprocessing.current_process().name
    if 'MainProcess' != pn and len(pn.split('-')) > 1:
        for h in logger.parent.handlers:
            if type(h) == RotatingFileHandler:
                logfile = '{}_{}.log'.format(h.baseFilename.rstrip('.log'), pn.split('-')[1])
                _fh = RotatingFileHandler(logfile, "a", maxBytes=h.maxBytes,
                                                           backupCount=h.backupCount, encoding=h.encoding)
                _fh.setLevel(h.level)
                _fh.setFormatter(h.formatter)
                logger.parent.removeHandler(h)
                logger.parent.addHandler(_fh)
                logger.debug("change new logfile %s" % logfile)
    executor = BoundedThreadPoolExecutor(max_workers=32)
    while True:
        sp = spider_queue.get()
        future = executor.submit(sp.crawl, validator_queue)
        logger.info("%s crawl BEGIN" % sp.name)
        future.add_done_callback(crawl_callback)


class Scheduler(object):
    spider_queue = Queue(32)
    validator_queue = Queue(12800)

    def __init__(self):
        self._stop = False
        self.crawl_process = None
        self.validator_thread = None
        self.cron_thread = None
        self.validator_pool = BoundedThreadPoolExecutor(max_workers=256)

    def feed(self):
        last_crawl_time = datetime.now() - timedelta(minutes=50)
        while not self._stop:
            if self.validator_queue.qsize() < 100:
                i = 0
                # peewee 会对相同的查询进行缓存
                proxies = ProxyIP.select().where((ProxyIP.updated_at < datetime.now() - timedelta(minutes=5))
                                                 & (ProxyIP.https_weight > 0) & (ProxyIP.http_weight > 0))
                for p in proxies.execute():
                    self.validator_queue.put(p)
                    i += 1
                logger.info('proxy from db :{}'.format(i))
                if i < 500 and last_crawl_time < datetime.now() - timedelta(minutes=8):
                    for provider in all_providers:
                        self.spider_queue.put(provider())
                    last_crawl_time = datetime.now()
                    logger.info('spiders :{} in queue'.format(len(all_providers)))
                    time.sleep(10*len(all_providers))
            time.sleep(10)

    def schedule_thread(self):
        if get_config('squid'):
            logger.info('schedule squid enabled')
            sq = Squid()
            TimerJob(60*7, sq.reconfigure)
        self.feed()

    def validate_proxy_ip(self, p: ProxyIP):
        if ValidateManager.should_validate(p):
            v = ValidateManager(p)
            try:
                v.validate()
            except (KeyboardInterrupt, SystemExit):
                logger.info('KeyboardInterrupt terminates validate_proxy_ip()')
        else:
            logger.info('skip validate {}  '.format(p))

    def validate_ips(self):
        while True:
            try:
                proxy: ProxyIP = self.validator_queue.get()
                if not get_config('no_validate'):
                    # logger.debug("submit validate :%s" % proxy.ip)
                    self.validator_pool.submit(self.validate_proxy_ip, p=proxy)
                else:
                    logger.debug("no_validate :%s" % proxy.ip)
            except (KeyboardInterrupt, SystemExit):
                break

    def start(self):
        """
        Start the scheduler with processes for worker (fetching candidate proxies from different spiders),
        and validator threads for checking whether the fetched proxies are able to use.
        """
        logger.info('Scheduler starts...')
        self.crawl_process = Process(target=crawl_ips, args=(self.spider_queue, self.validator_queue))
        self.validator_thread = Thread(target=self.validate_ips)
        self.cron_thread = Thread(target=self.schedule_thread)

        self.crawl_process.daemon = True
        self.validator_thread.daemon = True
        self.cron_thread.daemon = True

        self.cron_thread.start()
        self.crawl_process.start()
        logger.info('crawl_process started')

        self.validator_thread.start()
        logger.info('validator_thread started')

    def join(self):
        # while (self.crawl_process and self.crawl_process.is_alive()) or (
        #         self.validator_thread and self.validator_thread.is_alive()):
        #     try:
        #         self.crawl_process.join()
        #         self.validator_thread.join()
        #     except (KeyboardInterrupt, SystemExit):
        #         break
        while True:
            if self.validator_queue.qsize() > 10:
                logger.warning('spider_queue:{}, validator_queue:{}'
                               .format(self.spider_queue.qsize(), self.validator_queue.qsize()))
            else:
                logger.info('spider_queue:{}, validator_queue:{}'
                            .format(self.spider_queue.qsize(), self.validator_queue.qsize()))
            time.sleep(4)

    def stop(self):
        self.crawl_process.terminate()
        self._stop = True
        self.spider_queue.close()
        self.validator_pool.shutdown(wait=False)
