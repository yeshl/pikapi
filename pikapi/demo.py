import logging
from concurrent.futures.thread import ThreadPoolExecutor
from time import sleep


logging.basicConfig(level=logging.DEBUG,
                    format='[%(asctime)s] <%(processName)s>%(threadName)s - [%(filename)s:%(lineno)s]%(levelname)5s : %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


def pw1(i):
    while True:
        print(i)
        sleep(1)


def pw2(i):
    while True:
        print('<%d>' % i)
        sleep(1)


def callback(future):
    try:
        rst = future.result()
    except Exception as e:
        logger.error("thread error %s", e, exc_info=True)


def test1(fun):
    pool = ThreadPoolExecutor(30)
    for i in range(10):
        pool.submit(fun, i).add_done_callback(callback)


if __name__ == '__main__':
    pool = ThreadPoolExecutor(30)
    pool.submit(pw1, 1).add_done_callback(callback)
    pool.submit(pw1, 3).add_done_callback(callback)
    pool.submit(pw2, 2).add_done_callback(callback)
    pool.submit(pw2, 4).add_done_callback(callback)