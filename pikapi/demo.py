import logging
import multiprocessing
import threading
from concurrent.futures.thread import ThreadPoolExecutor
from time import sleep

from pikapi.database import ProxyIP, create_connection, create_db_tables, ProxyWebSite, _db
from pikapi.sqlitedb import SqliteClient

logging.basicConfig(level=logging.DEBUG,
                    format='[%(asctime)s] <%(processName)s>%(threadName)s - [%(filename)s:%(lineno)s]%(levelname)5s : %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


def pw(i):

    while True:
        with _db.connection_context():
            proxies = ProxyIP.select(ProxyIP.ip).where((ProxyIP.https_weight > 0))
            proxies.execute()
        # for x in proxies.iterator():
        #     print(x.ip)
        sleep(2)


def pw2(i):
    while True:
        cnt = ProxyWebSite.update(proxy_count=0,
                                  last_fetch=ProxyWebSite.this_fetch,
                                  stats='oo') \
            .where(ProxyWebSite.site_name == 'site_name').execute()
        sleep(2)


def callback(future):
    try:
        rst = future.result()
    except Exception as e:
        logger.error("thread error %s", e, exc_info=True)


def test_fun_in_threadpool(fun):
    pool = ThreadPoolExecutor(30)
    for i in range(10):
        pool.submit(fun, i).add_done_callback(callback)


def test2():
    for i in range(1):
        p = multiprocessing.Process(target=pw2, args=(i,))
        p.start()


if __name__ == '__main__':
    db = create_connection()
    create_db_tables()
    test_fun_in_threadpool(pw)
    # test2()
