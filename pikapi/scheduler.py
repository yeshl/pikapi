import multiprocessing
import queue
import sys
import time
import schedule

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from multiprocessing import Queue, Process
from threading import Thread

from pikapi.config import get_config
from pikapi.database import ProxyIP, ProxyWebSite
from pikapi.spiders import *
from pikapi.validators.validate_manager import ValidateManager

logger = logging.getLogger(__name__)


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


def crawl_ips(spider_queue, validator_queue):
    # if sys.platform.startswith('linux'):
    pn = multiprocessing.current_process().name
    if 'MainProcess' != pn and len(pn.split('-')) > 1:
        for h in logger.parent.handlers:
            if type(h) == logging.handlers.RotatingFileHandler:
                logfile = '{}_{}.log'.format(h.baseFilename.rstrip('.log'), pn.split('-')[1])
                _fh = logging.handlers.RotatingFileHandler(logfile, "a", maxBytes=h.maxBytes,
                                                           backupCount=h.backupCount, encoding=h.encoding)
                _fh.setLevel(h.level)
                _fh.setFormatter(h.formatter)
                logger.parent.removeHandler(h)
                logger.parent.addHandler(_fh)
                logger.debug("change new logfile %s" % logfile)
    executor = BoundedThreadPoolExecutor(max_workers=32)
    while True:
        p = spider_queue.get()
        future = executor.submit(p.crawl, validator_queue)
        future.add_done_callback(crawl_callback)


class Scheduler(object):
    spider_queue = Queue(32)
    validator_queue = Queue(512)

    def __init__(self):
        self.crawl_process = None
        self.validator_thread = None
        self.cron_thread = None
        self.validator_pool = BoundedThreadPoolExecutor(max_workers=256)

    def feed_from_db(self):
        proxies = ProxyIP.select().where(ProxyIP.updated_at < datetime.now() - timedelta(minutes=15))
        for p in proxies.execute():
            self.validator_queue.put(p)
            # logger.debug('from database for validation: {}:{}'.format(p.ip, p.port))

    def feed_providers(self):
        if self.validator_queue.qsize() > 100:
            logger.warning('too many task in validator_queue {} , skip schedule crawl !!'
                           .format(self.validator_queue.qsize()))
        else:
            logger.debug('feed {} spiders...'.format(len(all_providers)))
            for provider in all_providers:
                self.spider_queue.put(provider())

    def cron_schedule(self):
        exit_flag = False
        self.feed_providers()
        schedule.every(10).minutes.do(self.feed_providers)

        self.feed_from_db()
        schedule.every(10).minutes.do(self.feed_from_db)

        logger.info('Start python scheduler')
        while not exit_flag:
            try:
                schedule.run_pending()
                time.sleep(4)
            except (KeyboardInterrupt, InterruptedError):
                logger.info('Stopping python scheduler')
                break

    def validate_proxy_ip(self, p: ProxyIP):
        if ValidateManager.should_validate(p):
            v = ValidateManager(p)
            try:
                v.validate()
            except (KeyboardInterrupt, SystemExit):
                logger.info('KeyboardInterrupt terminates validate_proxy_ip()' )
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
        self.cron_thread = Thread(target=self.cron_schedule)

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
        self.spider_queue.close()
        self.crawl_process.terminate()
        # self.validator_thread.terminate() # TODO: 'terminate' the thread using a flag
        self.validator_pool.shutdown(wait=False)


class BoundedThreadPoolExecutor(ThreadPoolExecutor):
    def __init__(self, max_workers=None, thread_name_prefix=''):
        super().__init__(max_workers, thread_name_prefix)
        self._work_queue = queue.Queue(max_workers)
