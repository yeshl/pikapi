import logging
import unittest

import pikapi.database
from pikapi.database import ProxyWebSite, create_db_tables
from pikapi.spiders import *
from pikapi.spiders.spider import Spider

logger = logging.getLogger('pikapi.test')


class TestProvider(unittest.TestCase):
    def test(self):
        create_db_tables()
        self.assert_provider(Spider31f())
        # self.assert_provider(SpiderGoubanjia())
        # self.assert_provider(SpiderFeilong())
        # self.assert_provider(SpiderIp3366())
        # self.assert_provider(SpiderIphai())
        # self.assert_provider(Spider89ip())
        # self.assert_provider(SpiderCnProxy())
        # self.assert_provider(SpiderCoolProxy())
        # self.assert_provider(Spider66ip())
        # self.assert_provider(SpiderA2u())
        # self.assert_provider(SpiderData5u())
        # self.assert_provider(SpiderIpaddress())
        # self.assert_provider(SpiderKuaidaili())
        # self.assert_provider(SpiderMrhinkydink())
        # self.assert_provider(SpiderClarketm())
        # self.assert_provider(SpiderXici())
        # for p in all_providers:
        #     self.assert_provider(p())

    def assert_provider(self, p: Spider):
        provider, obj, exc = p.crawl(None)
        proxies = list(set(provider.proxies))
        pw: ProxyWebSite = ProxyWebSite(site_name=provider.name)
        if exc is None:
            pw.stats = 'OK'
        else:
            # pw.stats = exc.arg[0]
            pw.stats = exc.__class__.__name__
            logger.error("crawl error:%s", str(exc))

        pw.proxy_count = len(proxies)
        logger.debug("{} crawl proxies:{}".format(provider.name, pw.proxy_count))
        for i, v in enumerate(proxies):
            logger.debug("[{0}] {1}:{2}".format(i, v[0], v[1]))
        pw.merge()


if __name__ == '__main__':
    unittest.main()
    # suit = unittest.TestSuite()
    # suit.addTest(ProviderTest("test"))
    # runner = unittest.TextTestRunner()
    # runner.run()