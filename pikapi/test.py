import queue
import time
from concurrent.futures import ThreadPoolExecutor, Future
from multiprocessing import Queue


def f(i):
    time.sleep(10)
    print(i)


def tt():
    pool = BoundedThreadPoolExecutor(2)
    for i in range(1, 1000):
        print('提交任务%d' % i)
        pool.submit(f, (1))
    while True:
        time.sleep(1)
        print('main')


class BoundedThreadPoolExecutor(ThreadPoolExecutor):
    def __init__(self, max_workers=None, thread_name_prefix=''):
        super().__init__(max_workers,thread_name_prefix)
        self._work_queue = queue.Queue(max_workers)


if __name__ == "__main__":
    tt()
