import re

from lxml import etree
from pyquery import PyQuery

from pikapi.spiders.spider import Spider


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
    start_urls =['http://www.xicidaili.com/{}/{}'.format(c, i) for c in ['nn', 'wn', 'wt'] for i in range(1, 4)]

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


class SpiderIp3366(Spider):
    name = 'www.ip3366.net'
    start_urls = ['http://www.ip3366.net/free/?stype=1&page=%s' % i for i in range(1, 8)]

    def parse(self, html):
        doc = PyQuery(html)
        trs = doc('.table > tbody:nth-child(2) > tr')
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
    start_urls = ['https://31f.cn/http-proxy/','https://31f.cn/https-proxy/']

    def parse(self, html):
        doc = PyQuery(html)
        trs = doc('table.table > tr')
        for t in trs.items():
            ip = t('td').eq(1).text()
            port = t('td').eq(2).text()
            if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', ip):
                self._proxies.append((ip, port))
