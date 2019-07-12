import time
import schedule

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from multiprocessing import Queue, Process
from threading import Thread
from pikapi.config import get_config
from pikapi.database import ProxyIP, ProxyWebSite
from pikapi.loggings import logger
from pikapi.providers import *
from pikapi.validate_manager import ValidateManager


def crawl_ips(provider_queue: Queue, validator_queue: Queue):
    while True:
        p: BaseProvider = provider_queue.get()
        pw: ProxyWebSite = ProxyWebSite(site_name=p.site_name)
        logger.error("{} crawling...".format(p))
        pw.stats = 'OK'
        try:
            proxies = p.crawl()
            pw.proxy_count = len(proxies)
            logger.error("{} crawl proxies:{}".format(p.site_name, pw.proxy_count))
            for p in proxies:
                validator_queue.put(ProxyIP(ip=p[0], port=p[1]))
        except Exception as e:
            logger.error("{} crawl error:{}".format(p.site_name, e))
            pw.stats = e .__class__.__name__
        finally:
            pw.merge()


def validate_proxy_ip(p: ProxyIP):
    v = ValidateManager(p)
    try:
        v.validate()
    except (KeyboardInterrupt, SystemExit):
        logger.info('KeyboardInterrupt terminates validate_proxy_ip: ' + p.ip)


def validate_ips(validator_queue: Queue, validator_pool: ThreadPoolExecutor):
    while True:
        try:
            proxy: ProxyIP = validator_queue.get()
            validator_pool.submit(validate_proxy_ip, p=proxy)
        except (KeyboardInterrupt, SystemExit):
            break


def cron_schedule(scheduler):
    """
    :param scheduler: the Scheduler instance
    """
    exit_flag = False

    def feed():
        scheduler.feed_providers()

    def feed_from_db():
        proxies = ProxyIP.select().where(ProxyIP.updated_at < datetime.now() - timedelta(minutes=15))
        for p in proxies.execute():
            scheduler.validator_queue.put(p)
            logger.debug('from database for validation: {}{}:{}' \
                         .format('https://' if p.is_https else 'http://', p.ip, p.port))

    scheduler.feed_providers()
    feed_from_db()
    schedule.every(15).minutes.do(feed)
    schedule.every(7).minutes.do(feed_from_db)
    logger.info('Start python scheduler')

    while not exit_flag:
        try:
            schedule.run_pending()
            time.sleep(7)
        except (KeyboardInterrupt, InterruptedError):
            logger.info('Stopping python scheduler')
            break


class Scheduler(object):
    def __init__(self):
        self.worker_queue = Queue()
        self.validator_queue = Queue()
        self.worker_process = None
        self.validator_thread = None
        self.cron_thread = None
        self.validator_pool = ThreadPoolExecutor(max_workers=int(get_config('validation_pool', default='31')))

    def start(self):
        """
        Start the scheduler with processes for worker (fetching candidate proxies from different providers),
        and validator threads for checking whether the fetched proxies are able to use.
        """
        logger.info('Scheduler starts...')
        self.cron_thread = Thread(target=cron_schedule, args=(self,), daemon=True)
        # self.worker_process = Process(target=crawl_ips, args=(self.worker_queue, self.validator_queue))
        self.worker_process = Thread(target=crawl_ips, args=(self.worker_queue, self.validator_queue))
        self.validator_thread = Thread(target=validate_ips, args=(self.validator_queue, self.validator_pool))

        self.cron_thread.daemon = True
        self.worker_process.daemon = True
        self.validator_thread.daemon = True

        self.cron_thread.start()
        self.worker_process.start()  # Python will wait for all process finished
        logger.info('worker_process started')
        self.validator_thread.start()
        logger.info('validator_thread started')

    def join(self):
        """
        Wait for worker processes and validator threads

        """
        while (self.worker_process and self.worker_process.is_alive()) or (
                self.validator_thread and self.validator_thread.is_alive()):
            try:
                self.worker_process.join()
                self.validator_thread.join()
            except (KeyboardInterrupt, SystemExit):
                break

    def feed_providers(self):
        logger.debug('feed {} providers...'.format(len(all_providers)))

        for provider in all_providers:
            self.worker_queue.put(provider())

    def stop(self):
        self.worker_queue.close()
        self.worker_process.terminate()
        # self.validator_thread.terminate() # TODO: 'terminate' the thread using a flag
        self.validator_pool.shutdown(wait=False)
