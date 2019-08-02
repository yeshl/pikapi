import base64
import logging
import re
import time

import requests
from lxml import etree
from pyquery import PyQuery
from pikapi.spiders.spider import Spider

logger = logging.getLogger(__name__)


class SpiderA2u(Spider):
    name = 'githubusercontent.com/a2u'
    start_urls = ['https://raw.githubusercontent.com/a2u/free-proxy-list/master/free-proxy-list.txt']

    def parse(self, text):
        lst = re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{2,5}', text)
        for it in lst:
            ip, port = it.split(':')
            if ip and port:
                self._proxies.append((ip, port))


class SpiderClarketm(Spider):
    name = 'githubusercontent.com/clarketm'
    start_urls = ['https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list.txt']

    def parse(self, html):
        ip_port_str_list = re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{2,5}', html)
        for ip_port in ip_port_str_list:
            ip = re.search(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', ip_port).group(0)
            port = re.search(r':(\d{2,5})', ip_port).group(1)
            if ip and port:
                self._proxies.append((ip, port))


class SpiderData5u(Spider):
    name = 'www.data5u.com'
    start_urls = [
        'http://www.data5u.com'
    ]

    def parse(self, html):
        doc = PyQuery(html)
        info = doc("ul.l2")
        for tr in info.items():
            ip = tr("span:first-child").text()
            port = tr("span").eq(1).text()
            self._proxies.append((ip, port))


class SpiderIpaddress(Spider):
    name = 'www.ipaddress.com'
    start_urls = [
        'https://www.ipaddress.com/proxy-list/'
    ]

    def parse(self, html):
        doc = PyQuery(html)
        trs = doc("body > div.resp.main > main > table > tbody > tr")
        for tr in trs.items():
            ip = tr("td").eq(0).text().split(':')
            self._proxies.append((ip[0], ip[1]))


class SpiderKuaidaili(Spider):
    name = 'www.kuaidaili.com'
    # start_urls = ['https://www.kuaidaili.com/free/inha/1']
    start_urls = ['https://www.kuaidaili.com/free/inha/%s' % i for i in range(1, 6)] + \
                 ['https://www.kuaidaili.com/proxylist/%s' % i for i in range(1, 11)]

    def parse(self, html):
        doc = PyQuery(html)
        rows = doc('#list table tr')
        if len(rows) == 0:
            rows = doc('#freelist table tr')
        for ip_row in rows.items():
            ip = ip_row('td').eq(0).text()
            port = ip_row('td').eq(1).text()
            if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', ip):
                self._proxies.append((ip, port))


class SpiderMrhinkydink(Spider):
    name = 'www.mrhinkydink.com'
    start_urls = ['http://www.mrhinkydink.com/proxies.htm',
                  'http://www.mrhinkydink.com/proxies2.htm',
                  'http://www.mrhinkydink.com/proxies3.htm'
                  ]

    def parse(self, html):
        doc = PyQuery(html)
        trs = doc("tr.text")
        for t in trs.items():
            ip = t('td').eq(0).text()
            port = t('td').eq(1).text()
            if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', ip):
                self._proxies.append((ip, port))


class SpiderXici(Spider):
    name = 'www.xicidaili.com'
    start_urls = ['http://www.xicidaili.com/{}/{}'.format(c, i) for c in ['nn', 'wn', 'wt'] for i in range(1, 4)]

    def parse(self, html):
        doc = PyQuery(html)
        trs = doc("#ip_list tr")
        for t in trs.items():
            ip = t('td').eq(1).text()
            port = t('td').eq(2).text()
            if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', ip):
                self._proxies.append((ip, port))


class SpiderCnProxy(Spider):
    name = 'cn-proxy.com'
    start_urls = ['https://cn-proxy.com/']

    def parse(self, html):
        doc = PyQuery(html)
        trs = doc("div.table-container > table:nth-child(1) > tbody:nth-child(3) > tr")
        for t in trs.items():
            ip = t('td').eq(0).text()
            port = t('td').eq(1).text()
            if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', ip):
                self._proxies.append((ip, port))


class Spider89ip(Spider):
    name = 'www.89ip.cn'
    # start_urls = ['http://www.89ip.cn/']
    start_urls = ['http://www.89ip.cn/index_%s.html' % i for i in range(1, 17)]

    def parse(self, html):
        doc = PyQuery(html)
        trs = doc('.layui-table > tbody:nth-child(2) > tr')
        for t in trs.items():
            ip = t('td').eq(0).text()
            port = t('td').eq(1).text()
            if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', ip):
                self._proxies.append((ip, port))


class SpiderIphai(Spider):
    name = 'www.iphai.com'
    start_urls = ['http://www.iphai.com/',
                  'http://www.iphai.com/free/ng',
                  'http://www.iphai.com/free/np',
                  'http://www.iphai.com/free/wg']

    def parse(self, html):
        doc = PyQuery(html)
        trs = doc('.table > tr')
        for t in trs.items():
            ip = t('td').eq(0).text()
            port = t('td').eq(1).text()
            if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', ip):
                self._proxies.append((ip, port))


class SpiderFeilong(Spider):
    name = 'www.feilongip.com'
    start_urls = ['http://www.feilongip.com/']

    def parse(self, html):
        doc = PyQuery(html)
        trs = doc('.FreeIptbody > tr')
        for t in trs.items():
            ip = t('td').eq(1).text().split(':')
            if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', ip[0]):
                self._proxies.append((ip[0], ip[1]))


class Spider31f(Spider):
    name = '31f.cn'
    start_urls = ['https://31f.cn/http-proxy/', 'https://31f.cn/https-proxy/']

    def parse(self, html):
        doc = PyQuery(html)
        trs = doc('table.table > tr')
        for t in trs.items():
            ip = t('td').eq(1).text()
            port = t('td').eq(2).text()
            if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', ip):
                self._proxies.append((ip, port))


class SpiderIp3366(Spider):
    name = 'www.ip3366.net'
    start_urls = ['http://www.ip3366.net/free/?stype={0}&page={1}'.format(i, j)
                  for i in range(1, 7) for j in range(1, 7)]

    def parse(self, html):
        doc = PyQuery(html)
        trs = doc('table > tbody > tr')
        for t in trs.items():
            ip = t('td').eq(0).text()
            port = t('td').eq(1).text()
            if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', ip):
                self._proxies.append((ip, port))


class SpiderProxy_listen(Spider):
    name = 'www.proxy-listen.de'
    start_urls = ['https://www.proxy-listen.de/Proxy/Proxyliste.html']

    def crawl(self, obj):
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

    def parse(self, html):
        doc = PyQuery(html)
        trs = doc('table.proxyList > tr')
        for t in trs.items():
            ip = t('td').eq(0).text()
            port = t('td').eq(1).text()
            if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', ip):
                self._proxies.append((ip, port))


class _SpiderMimvp(Spider):
    # 端口为图片
    name = 'proxy.mimvp.com'
    start_urls = ['https://proxy.mimvp.com/free.php?proxy=in_hp',
                  'https://proxy.mimvp.com/free.php?proxy=in_tp']

    def img2code(self, imgurl):
        ir = requests.get(imgurl, headers=self._headers, timeout=10)
        if ir.status_code == 200:
            post_data = {"image": base64.b64encode(ir.content)}
            res = requests.post(self.crack_url, data=post_data)  # TODO:
            return res.text

    def parse(self, html):
        doc = PyQuery(html)
        trs = doc('.free-table > tbody > td.tbl-proxy-ip,.tbl-proxy-port')
        for t in trs.items():
            ip = t('td.tbl-proxy-ip').text()
            img = t('td.tbl-proxy-port > img').attr('src')  # 端口为图片需要进行识别
            port = self.img2code(img)
            if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', ip):
                self._proxies.append((ip, port))


class SpiderProxylistplus(Spider):
    name = 'proxylistplus.com'
    start_urls = ["https://list.proxylistplus.com/Fresh-HTTP-Proxy-List-{0}".format(i) for i in range(1, 7)]

    def parse(self, html):
        doc = PyQuery(html)
        trs = doc('tr.cells')
        for t in trs.items():
            ip = t('td').eq(1).text()
            port = t('td').eq(2).text()
            if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', ip):
                self._proxies.append((ip, port))


class SpiderTxt(Spider):
    name = 'txt.com'
    start_urls = [
            # "http://www.proxylists.net/http_highanon.txt",
            # "http://ab57.ru/downloads/proxylist.txt",
            # "http://ab57.ru/downloads/proxyold.txt",
            # "http://pubproxy.com/api/proxy?limit=20&format=txt&type=http",
            # "http://comp0.ru/downloads/proxylist.txt",
            # 'https://www.rmccurdy.com/scripts/proxy/good.txt'
            # 'http://www.atomintersoft.com/anonymous_proxy_list',
            'http://www.atomintersoft.com/high_anonymity_elite_proxy_list'
        ]

    def parse(self, html):
        lst = re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{2,5}', html)
        for it in lst:
            ip, port = it.split(':')
            if ip and port:
                self._proxies.append((ip, port))


class SpiderJiangxianli(Spider):
    name = 'ip.jiangxianli.com'
    start_urls = ['http://ip.jiangxianli.com/?page={}'.format(i) for i in range(1, 4)]

    def parse(self, html):
        doc = PyQuery(html)
        trs = doc('table > tbody > tr')
        for t in trs.items():
            ip = t('td').eq(1).text()
            port = t('td').eq(2).text()
            if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', ip):
                self._proxies.append((ip, port))


class SpiderKxdaili(Spider):
    name = 'kxdaili.com'
    start_urls = ['http://www.kxdaili.com/dailiip/%s/%s.html#ip' % (i, j) for i in range(1, 3) for j in range(1, 11)]

    def parse(self, html):
        doc = PyQuery(html)
        trs = doc('table > tbody > tr')
        for t in trs.items():
            ip = t('td').eq(0).text()
            port = t('td').eq(1).text()
            if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', ip):
                self._proxies.append((ip, port))