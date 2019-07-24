import unittest

from pikapi.database import ProxyWebSite
from pikapi.providers import *
from pikapi.providers._66ip_provider import _66ipProvider
from pikapi.providers.mrhinkydink_provider import MrhinkydinkProvider


class TestProvider(unittest.TestCase):
    def test(self):
        # self.assert_provider(A2uProvider())
        #self.assert_provider(CoolProxyProvider())
        # self.assert_provider(Data5uProvider())
        # self.assert_provider(FreeProxyListProvider())
        #self.assert_provider(HttpProxyProvider())
        # self.assert_provider(SpyMeProvider())
        # self.assert_provider(SpysOneProvider())
        # self.assert_provider(IpaddressProvider())
        #self.assert_provider(KuaidailiProvider())
        # self.assert_provider(MrhinkydinkProvider())
        self.assert_provider(_66ipProvider())
        # self.assert_provider(XiciProvider())
        # for p in all_providers:
        #     self.assert_provider(p())

    def assert_provider(self, p: BaseProvider):
        pw: ProxyWebSite = ProxyWebSite(p.site_name)
        print("{} crawling...".format(p))
        err = 'OK'
        proxies = []
        try:
            proxies = p.crawl()
            proxies = set(proxies)
            pw.proxy_count = len(proxies)
        except Exception as e:
            print("{} crawl error:{}".format(p.site_name, e))
            err = e.__class__.__name__
            pw.stats = err
        finally:
            print(pw)
            for i, v in enumerate(proxies):
                print("[{0}] {1}:{2}".format(i, v[0], v[1]))


if __name__ == '__main__':
    unittest.main()
    # suit = unittest.TestSuite()
    # suit.addTest(ProviderTest("test"))
    # runner = unittest.TextTestRunner()
    # runner.run()
