from concurrent.futures import ThreadPoolExecutor, Future


def f(*i):
    exc = None
    try:
        i[1].hi += 1
        a=1/0
    except Exception as e:
        exc = e
    return i, exc


def callback(future: Future):
    tpl, exc = future.result()
    print('error:'+ exc.args[0])
    for i in tpl:
        print(i)


class abc(object):
    hi = 0

    def __str__(self):
        return '{},{}'.format(self.__class__.__name__, self.hi)


if __name__ == "__main__":
    pool = ThreadPoolExecutor(3)
    obj = abc()
    print(obj)
    pool.submit(f, *(1, obj, 3)).add_done_callback(callback)
