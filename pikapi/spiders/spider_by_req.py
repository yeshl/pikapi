import logging
import re
import time

import requests
from pyquery import PyQuery

from pikapi.spiders.spider import Spider

logger = logging.getLogger(__name__)


class SpiderTxt(Spider):
    name = 'txt'
    start_urls = [
        "http://www.proxylists.net/http_highanon.txt",
        "http://ab57.ru/downloads/proxylist.txt",
        "http://ab57.ru/downloads/proxyold.txt",
        "http://pubproxy.com/api/proxy?limit=20&format=txt&type=http",
        "http://comp0.ru/downloads/proxylist.txt",
        'https://www.rmccurdy.com/scripts/proxy/good.txt',
        'http://www.atomintersoft.com/anonymous_proxy_list',
        'https://raw.githubusercontent.com/a2u/free-proxy-list/master/free-proxy-list.txt',
        'http://www.atomintersoft.com/high_anonymity_elite_proxy_list',
        'https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list.txt'
    ]

    def parse(self, html):
        lst = re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{2,5}', html)
        for it in lst:
            ip, port = it.split(':')
            if ip and port:
                self._proxies.append((ip, port))


class SpiderData5u(Spider):
    name = 'www.data5u.com'
    start_urls = ['http://www.data5u.com']
    parse_args = ('ul.l2', 'span', 0, 1)


class SpiderIpaddress(Spider):
    name = 'www.ipaddress.com'
    start_urls = ['https://www.ipaddress.com/proxy-list/']
    parse_args = ('table > tbody > tr', 'td', 0, -1)


class SpiderKuaidaili(Spider):
    name = 'www.kuaidaili.com'
    # start_urls = ['https://www.kuaidaili.com/free/inha/1']
    start_urls = ['https://www.kuaidaili.com/free/inha/%s' % i for i in range(1, 6)] + \
                 ['https://www.kuaidaili.com/proxylist/%s' % i for i in range(1, 11)]


class SpiderMrhinkydink(Spider):
    name = 'www.mrhinkydink.com'
    start_urls = ['http://www.mrhinkydink.com/proxies.htm',
                  'http://www.mrhinkydink.com/proxies2.htm',
                  'http://www.mrhinkydink.com/proxies3.htm'
                  ]
    parse_args = ('table > tr', 'td', 0, 1)
    # parse_args = ('tr.text',  'td', 0, 1)


class SpiderXici(Spider):
    name = 'www.xicidaili.com'
    start_urls = ['http://www.xicidaili.com/{}/{}'.format(c, i) for c in ['nn', 'wn', 'wt'] for i in range(1, 4)]
    parse_args = ('#ip_list tr', 'td', 1, 2)


class SpiderCnProxy(Spider):
    name = 'cn-proxy.com'
    start_urls = ['https://cn-proxy.com/']
    parse_args = ('div.table-container > table:nth-child(1) > tbody:nth-child(3) > tr', 'td', 0, 1)


class Spider89ip(Spider):
    name = 'www.89ip.cn'
    # start_urls = ['http://www.89ip.cn/']
    start_urls = ['http://www.89ip.cn/index_%s.html' % i for i in range(1, 17)]


class SpiderIphai(Spider):
    name = 'www.iphai.com'
    start_urls = ['http://www.iphai.com/',
                  'http://www.iphai.com/free/ng',
                  'http://www.iphai.com/free/np',
                  'http://www.iphai.com/free/wg']
    parse_args = ('table > tr', 'td', 0, 1)


class SpiderFeilong(Spider):
    name = 'www.feilongip.com'
    start_urls = ['http://www.feilongip.com/']
    parse_args = ('.FreeIptbody > tr', 'td', 1, -1)


class Spider31f(Spider):
    name = '31f.cn'
    start_urls = ['https://31f.cn/http-proxy/', 'https://31f.cn/https-proxy/']
    parse_args = ('table.table > tr', 'td', 1, 2)


class SpiderIp3366(Spider):
    name = 'www.ip3366.net'
    start_urls = ['http://www.ip3366.net/free/?stype={0}&page={1}'.format(i, j)
                  for i in range(1, 7) for j in range(1, 7)]


class SpiderProxyListen(Spider):
    name = 'www.proxy-listen.de'
    start_urls = ['https://www.proxy-listen.de/Proxy/Proxyliste.html']
    parse_args = ('table.proxyList > tr', 'td', 0, 1)

    def crawl(self, obj=None):
        exc = None
        self._session = requests.session()
        try:
            for url in self.start_urls:
                logger.debug('requests {}'.format(url))
                resp = self._session.get(url, headers=self._headers, timeout=self._req_timeout, verify=False)
                key_pattern = re.compile('''name="fefefsfesf4tzrhtzuh" value="([^"]+)"''')
                keysearch = re.findall(key_pattern, resp.text)
                data = {"filter_port": "", "filter_http_gateway": "", "filter_http_anon": "",
                        "filter_response_time_http": "", "fefefsfesf4tzrhtzuh": keysearch[0],
                        "filter_country": "", "filter_timeouts1": "", "liststyle": "info", "proxies": "300",
                        "type": "httphttps", "submit": "Show"}

                resp = self._session.post(url, headers=self._headers, data=data, timeout=self._req_timeout,
                                          verify=False)
                resp.encoding = self._encoding
                if resp.status_code == 200:
                    self.parse(resp.text)
                    logger.debug('{} crawl proxies: {}'.format(url, len(self._proxies)))
                else:
                    logger.error("response code：{} from {}".format(resp.status_code, url))
                time.sleep(self._sleep)
        except Exception as e:
            exc = e
        finally:
            self._session.close()

        return self, obj, exc


# class SpiderMimvp(Spider):
#     # 端口为图片
#     name = 'proxy.mimvp.com'
#     start_urls = ['https://proxy.mimvp.com/free.php?proxy=in_hp',
#                   'https://proxy.mimvp.com/free.php?proxy=in_tp']
#     crack_url = None
#
#     def img2code(self, imgurl):
#         ir = requests.get(imgurl, headers=self._headers, timeout=10)
#         if ir.status_code == 200:
#             post_data = {"image": base64.b64encode(ir.content)}
#             res = requests.post(self.crack_url, data=post_data)
#             return res.text
#
#     def parse(self, html):
#         doc = PyQuery(html)
#         trs = doc('.free-table > tbody > td.tbl-proxy-ip,.tbl-proxy-port')
#         for t in trs.items():
#             ip = t('td.tbl-proxy-ip').text()
#             img = t('td.tbl-proxy-port > img').attr('src')  # 端口为图片需要进行识别
#             port = self.img2code(img)
#             if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', ip):
#                 self._proxies.append((ip, port))

# class SpiderIpjing(Spider):
#     # 端口为图片
#     name = 'www.ipjing.com'
#     start_urls = ['https://www.ipjing.com//?page={}'.format(i) for i in range(1, 7)]


class SpiderProxylistplus(Spider):
    name = 'proxylistplus.com'
    start_urls = ["https://list.proxylistplus.com/Fresh-HTTP-Proxy-List-{0}".format(i) for i in range(1, 7)]
    parse_args = ('tr.cells', 'td', 1, 2)


class SpiderJiangxianli(Spider):
    name = 'ip.jiangxianli.com'
    start_urls = ['http://ip.jiangxianli.com/?page={}'.format(i) for i in range(1, 4)]
    parse_args = ('table > tbody > tr', 'td', 1, 2)


class SpiderKxdaili(Spider):
    name = 'kxdaili.com'
    start_urls = ['http://www.kxdaili.com/dailiip/%s/%s.html#ip' % (i, j) for i in range(1, 3) for j in range(1, 11)]


class SpiderCrossincode(Spider):
    name = 'lab.crossincode.com'
    start_urls = ['https://lab.crossincode.com/proxy/']
    parse_args = ('table > tr', 'td', 0, 1)


class SpiderXsdaili(Spider):
    name = 'www.xsdaili.com'
    start_urls = ['http://www.xsdaili.com/']
    parse_args = ('.cont', 'br', 0, 1)

    def setUp(self):
        html = self.reqs(self.start_urls[0])
        doc = PyQuery(html)
        tabs = doc('div.table')
        self.start_urls.clear()
        for i, t in enumerate(tabs.items()):
            a = t('div:nth-child(1) > a')
            # print(i, a.attr('href'), a.text())
            self.start_urls.append('http://www.xsdaili.com%s' % a.attr('href'))
            if i > 2:
                break

    def parse(self, html):
        lst = re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{2,5}', html)
        for it in lst:
            ip, port = it.split(':')
            if ip and port:
                self._proxies.append((ip, port))


class SpiderZdaye(SpiderXsdaili):
    name = 'ip.zdaye.com'
    start_urls = ['http://ip.zdaye.com/dayProxy.html']
    parse_args = ('.cont', 'br', 0, 1)

    def setUp(self):
        html = self.reqs(self.start_urls[0])
        doc = PyQuery(html)
        tabs = doc('div.thread_item')
        self.start_urls.clear()
        for i, t in enumerate(tabs.items()):
            a = t('div:nth-child(1) > h3 > a')
            self.start_urls.append('http://www.xsdaili.com%s' % a.attr('href'))
            if i > 2:
                break


class SpiderSuperfastip(Spider):
    name = 'www.superfastip.com'
    start_urls = ['http://www.superfastip.com/welcome/freeip/{}'.format(i) for i in range(1, 5)]


class SpiderYqie(Spider):
    name = 'ip.yqie.com'
    start_urls = ['http://ip.yqie.com/proxygaoni/',
                  'http://ip.yqie.com/proxypuni/',
                  'http://ip.yqie.com/proxyhttps/',
                  'http://ip.yqie.com/proxyhttp/'
                  ]
    parse_args = ('#GridViewOrder > tr', 'td', 1, 2)


class SpiderXiladaili(Spider):
    name = 'www.xiladaili.com'
    start_urls = ['http://www.xiladaili.com/gaoni/{}/'.format(i) for i in range(1, 5)] + \
                 ['http://www.xiladaili.com/http/{}/'.format(i) for i in range(1, 5)] + \
                 ['http://www.xiladaili.com/https/{}/'.format(i) for i in range(1, 5)]
    parse_args = ('.fl-table > tbody > tr', 'td', 0, -1)
