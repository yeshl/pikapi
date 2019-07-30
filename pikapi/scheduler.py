import time
import schedule

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from multiprocessing import Queue, Process
from threading import Thread

from pyppeteer import launch

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
    logger.debug("{} crawl proxies:{}".format(provider.name, pw.proxy_count))
    for p in proxies:
        validator_queue.put(ProxyIP(ip=p[0], port=p[1]))
    pw.merge()


def crawl_ips(spider_queue, validator_queue):
    executor = ThreadPoolExecutor(max_workers=32)
    while True:
        p = spider_queue.get()
        logger.debug("spider ready:%s", p)
        future = executor.submit(p.crawl, validator_queue)
        future.add_done_callback(crawl_callback)


class Scheduler(object):
    spider_queue = Queue()
    validator_queue = Queue()

    def __init__(self):
        self.worker_process = None
        self.validator_thread = None
        self.cron_thread = None
        self.validator_pool = ThreadPoolExecutor(max_workers=128)

    def feed_from_db(self):
        proxies = ProxyIP.select().where(ProxyIP.updated_at < datetime.now() - timedelta(minutes=15))
        for p in proxies.execute():
            self.validator_queue.put(p)
            # logger.debug('from database for validation: {}:{}'.format(p.ip, p.port))

    def feed_providers(self):
        logger.debug('feed {} spiders...'.format(len(all_providers)))
        for provider in all_providers:
            self.spider_queue.put(provider())

    def cron_schedule(self):
        exit_flag = False
        self.feed_providers()
        schedule.every(15).minutes.do(self.feed_providers)

        self.feed_from_db()
        schedule.every(7).minutes.do(self.feed_from_db)

        logger.info('Start python scheduler')
        while not exit_flag:
            try:
                schedule.run_pending()
                time.sleep(7)
            except (KeyboardInterrupt, InterruptedError):
                logger.info('Stopping python scheduler')
                break

    def validate_proxy_ip(self, p: ProxyIP):
        if ValidateManager.should_validate(p):
            v = ValidateManager(p)
            try:
                v.validate()
            except (KeyboardInterrupt, SystemExit):
                logger.info('KeyboardInterrupt terminates validate_proxy_ip: ' + p.ip)
        else:
            logger.info('skip validate {}  '.format(p.ip))

    def validate_ips(self):
        while True:
            try:
                proxy: ProxyIP = self.validator_queue.get()
                self.validator_pool.submit(self.validate_proxy_ip, p=proxy)
            except (KeyboardInterrupt, SystemExit):
                break

    def start(self):
        """
        Start the scheduler with processes for worker (fetching candidate proxies from different spiders),
        and validator threads for checking whether the fetched proxies are able to use.
        """
        logger.info('Scheduler starts...')
        self.worker_process = Process(target=crawl_ips, args=(self.spider_queue, self.validator_queue))
        self.validator_thread = Thread(target=self.validate_ips)
        self.cron_thread = Thread(target=self.cron_schedule)

        self.worker_process.daemon = True
        self.validator_thread.daemon = True
        self.cron_thread.daemon = True

        self.cron_thread.start()
        self.worker_process.start()
        logger.info('spider_process started')
        if not get_config('no_validation'):
            self.validator_thread.start()
            logger.info('validator_thread started')

    def join(self):
        while (self.worker_process and self.worker_process.is_alive()) or (
                self.validator_thread and self.validator_thread.is_alive()):
            try:
                self.worker_process.join()
                self.validator_thread.join()
            except (KeyboardInterrupt, SystemExit):
                break

    def stop(self):
        self.spider_queue.close()
        self.worker_process.terminate()
        # self.validator_thread.terminate() # TODO: 'terminate' the thread using a flag
        self.validator_pool.shutdown(wait=False)
