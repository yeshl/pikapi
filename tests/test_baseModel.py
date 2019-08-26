from datetime import datetime, timedelta
from unittest import TestCase
from random import randint

from pikapi.store import ProxyWebSite, BaseModel, ProxyIP


class TestBaseModel(TestCase):

    def testProxyWebSite(self):
        p = ProxyWebSite(site_name='www.ysl.com', proxy_count=10)
        p.save()
        self.assertIn(p.site_name, p.store)
        print(p)
        pw = ProxyWebSite.get('www.ysl.com')  # type: ProxyWebSite

        pw.stats = 'NMC'
        pw.save()
        self.assertEqual(ProxyWebSite.get('www.ysl.com').stats, pw.stats)
        pw.delete_self()
        # ProxyWebSite.delete('www.ysl.com')
        self.assertNotIn(pw.site_name, p.store)
        print(pw)
        print(id(p.store))

    def testProxyIP(self):
        p = ProxyIP(ip='201.34.5.215', port=3128)
        p.save()
        self.assertIn(p.ip, p.store)
        print(p)
        pw = ProxyIP.get('201.34.5.215')  # type: ProxyIP
        pw.city = 'NMC'
        pw.save()
        self.assertEqual(ProxyIP.get('201.34.5.215').city, pw.city)
        ProxyIP.delete('201.34.5.215')
        self.assertNotIn(pw.ip, p.store)
        print(pw)
        print(id(p.store))

    def testProxyIPSelect(self):
        ps = [ProxyIP(ip='201.34.5.%i' % randint(1, 255), port=i, https_weight=i % 2) for i in range(10)]
        print(ps)
        self.assertTrue(10 == len(ps))
        dic={}
        for p in ps:
            p.save()
            dic[p.ip]=p

        for i in range(20):
            # proxies = ProxyIP.select(lambda x: (x.https_weight  > 0))
            proxies =list(filter(lambda x: (x.https_weight  > 0),dic.values()))
            # proxies = ProxyIP.select(lambda x: x.https_weight + x.http_weight > 0)
            print(proxies)
            self.assertTrue(5 == len(proxies))

            # ss = ProxyIP.select(None)
            # print(ss)
            # self.assertTrue(10 == len(ps))

    def testBug(self):
        ps = [ProxyIP(ip='201.34.5.%i' % randint(1, 255), port=i, https_weight=i % 2) for i in range(10)]
        dic = {}
        for p in ps:
            dic[p.ip] = p
        print(dic)
        proxies = list(filter(lambda x: (x.https_weight > 0), dic.values()))
        print(proxies)
        self.assertTrue(5 == len(proxies))