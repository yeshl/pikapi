import logging
import unittest

from pikapi.spiders import *
from pikapi.spiders.spider import Spider

logger = logging.getLogger('pikapi.test')





def add_test(provider):
    name = f"Test{provider.__name__}"

    def test_method(p):
        def fn(self):
            sp, obj, exc = p.crawl()
            proxies = list(set(p.proxies))
            self.assertTrue(exc is None, p.name + " : " + exc.__class__.__name__)
            self.assertGreater(len(proxies), 0, p.name)
            logger.debug("{} crawl proxies:{}".format(p.name, len(proxies)))
        return fn

    d = {'test_fun': test_method(provider())}
    cls = type(name, (unittest.TestCase,), d)
    globals()[name] = cls


if __name__ == '__main__':
    for p in all_providers:
        add_test(p)
    unittest.main()

