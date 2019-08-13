#!/usr/bin/env python
# -*- coding:utf-8 _*-
"""
@author:Administrator
@time: 2019/08/{DAY}
"""
import unittest

from pikapi.spiders import *


class TestProvider(unittest.TestCase):
    def setUp(self) -> None:
        pass

    def test(self):
        self.assert_provider(SpiderXici())
        # for p in all_providers:
        #     self.assert_provider(p())

    def assert_provider(self, p: Spider):
        provider, obj, exc = p.crawl()
        proxies = list(set(provider.proxies))
        self.assertTrue(exc is None, provider.name + " : " + exc.__class__.__name__)
        self.assertGreater(len(proxies), 0, provider.name)
        logger.info("{} crawl proxies:{}".format(provider.name, len(proxies)))
        for i, v in enumerate(proxies):
            logger.info("[{0}] {1}:{2}".format(i, v[0], v[1]))
            if i > 2:
                break
