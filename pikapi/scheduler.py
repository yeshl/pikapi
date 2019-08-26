import multiprocessing
import queue
import threading
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from logging.handlers import RotatingFileHandler
from threading import Thread

from pikapi.config import get_config
from pikapi.store import ProxyIP, ProxyWebSite
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


# 跨进程全局变量
RUNNING_SPIDERS = None
VALIDATOR_QUEUE = None


def crawl_callback(future):
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
        global VALIDATOR_QUEUE
        for p in proxies:
            VALIDATOR_QUEUE.put(ProxyIP(ip=p[0], port=p[1]))
        logger.info("{} proxies enqueue:{}".format(provider.name, pw.proxy_count))
    except Exception as e:
        pw.stats = e.__class__.__name__
        logger.debug("{} crawl callback error:{}".format(provider.name, exc))
    logger.info("{} proxies save to db:{}".format(provider.name, pw.proxy_count))
    pw.save()
    logger.info("{} crawl END".format(provider.name, pw.proxy_count))
    global RUNNING_SPIDERS
    RUNNING_SPIDERS.value -= 1


def crawl_ips(running_spiders, spider_queue, validator_queue):
    global RUNNING_SPIDERS
    RUNNING_SPIDERS = running_spiders
    global VALIDATOR_QUEUE
    VALIDATOR_QUEUE = validator_queue
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
                logger.info("change new logfile %s" % logfile)

    executor = BoundedThreadPoolExecutor(max_workers=32)
    while True:
        sp = spider_queue.get()
        future = executor.submit(sp.crawl)
        RUNNING_SPIDERS.value += 1
        future.add_done_callback(crawl_callback)


def callback(future):
    try:
        rst = future.result()
    except Exception as e:
        logger.info("callback error %s", e, exc_info=True)


class Scheduler(object):
    spider_queue = multiprocessing.Queue(32)
    validator_queue = multiprocessing.Queue(12800)
    running_spiders = multiprocessing.Value("i", 0)

    def __init__(self):
        self._stop = False
        self.crawl_process = None
        self.validator_thread = None
        self.cron_thread = None
        self.validator_pool = BoundedThreadPoolExecutor(max_workers=256)

    def feed(self):
        last_crawl_time = datetime.now() - timedelta(minutes=50)
        while not self._stop:
            logger.info('feed loop ...')
            try:
                if self.validator_queue.qsize() < 100:
                    i = 0
                    # proxies = ProxyIP.select().where((ProxyIP.updated_at < datetime.now() - timedelta(minutes=5))
                    #                                  & (ProxyIP.https_weight + ProxyIP.http_weight > 0))
                    proxies = ProxyIP.select(lambda x: x.updated_at < datetime.now() - timedelta(minutes=5)
                                                       and (x.https_weight + x.http_weight > 0))
                    for p in proxies:
                        Scheduler.validator_queue.put(p)
                        i += 1
                    logger.info('proxy from db enqueue:{}'.format(i))
                    if i < 500 and Scheduler.running_spiders.value == 0 \
                            and last_crawl_time < datetime.now() - timedelta(minutes=15):
                        for provider in all_providers:
                            Scheduler.spider_queue.put(provider())
                        last_crawl_time = datetime.now()
                        logger.info('spiders :{} enqueue'.format(len(all_providers)))
                        time.sleep(120)
            except (KeyboardInterrupt, SystemExit):
                break
            except Exception as ex:
                logger.error("error:%s", str(ex), exc_info=True)
            time.sleep(10)

    def schedule_thread(self):
        if get_config('squid'):
            logger.info('schedule squid enabled')
            sq = Squid()
            TimerJob(60 * 5, sq.reconfigure)
        self.feed()

    @staticmethod
    def validate_proxy_ip(p):
        if ValidateManager.should_validate(p):
            v = ValidateManager(p)
            try:
                v.validate()
            except (KeyboardInterrupt, SystemExit):
                logger.info('KeyboardInterrupt terminates validate_proxy_ip()')
        else:
            logger.debug('skip validate {}  '.format(p))

    def validate_ips(self):
        while True:
            try:
                proxy: ProxyIP = self.validator_queue.get()
                if not get_config('no_validate'):
                    # logger.debug("submit validate :%s" % proxy.ip)
                    task = self.validator_pool.submit(self.validate_proxy_ip, p=proxy)
                    task.add_done_callback(callback)
                else:
                    logger.debug("no_validate :%s" % proxy.ip)
            except (KeyboardInterrupt, SystemExit):
                break
            except Exception as ex:
                logger.error("error:%s", str(ex), exc_info=True)

    def start(self):
        """
        Start the scheduler with processes for worker (fetching candidate proxies from different spiders),
        and validator threads for checking whether the fetched proxies are able to use.
        """
        logger.info('Scheduler starts...')
        #这里使用独立进程采集，在linux上导致sqlite更新数据在此进程堵塞，不明原因
        # self.crawl_process = multiprocessing.Process(target=crawl_ips,
        #                                              args=(Scheduler.running_spiders,
        #                                                    Scheduler.spider_queue,
        #                                                    Scheduler.validator_queue))
        self.crawl_process = Thread(target=crawl_ips,
                                    args=(Scheduler.running_spiders,
                                          Scheduler.spider_queue,
                                          Scheduler.validator_queue))
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
            logger.info('<<< spider_queue:{}, validator_queue:{}, running_spider:{} >>>'
                        .format(self.spider_queue.qsize(), self.validator_queue.qsize(),
                                Scheduler.running_spiders.value))
            time.sleep(4)

    def stop(self):
        self.crawl_process.terminate()
        self._stop = True
        self.spider_queue.close()
        self.validator_pool.shutdown(wait=False)
