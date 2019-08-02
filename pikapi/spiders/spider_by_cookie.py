import logging
import re
import asyncio

from lxml import etree
from pikapi.spiders.spider import CookieSpider

logger = logging.getLogger(__name__)


class Spider66ip(CookieSpider):
    name = 'www.66ip.cn'
    # start_urls = ['http://www.66ip.cn/1.html']
    # start_urls = ['http://www.66ip.cn/%s.html' % i for i in range(1, 3)]
    start_urls = ['http://www.66ip.cn/%s.html' % i for i in range(1, 3)] + \
                 ['http://www.66ip.cn/areaindex_%s/%s.html' % (i, j) for i in range(1, 35) for j in range(1, 3)]

    def __init__(self):
        super().__init__()
        self._encoding = 'gbk'
        self._home_url = 'http://www.66ip.cn'

    def parse(self, text):
        # logger.debug(text)
        html = etree.HTML(text)
        table = html.xpath('//table/tr[position()>1]')
        for r in table:
            ip = r.xpath(".//td[1]/text()")[0]
            port = r.xpath(".//td[2]/text()")[0]
            if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', ip):
                self._proxies.append((ip, port))

class Spider66ipcn(CookieSpider):
    name = '66ip.cn'
    start_urls = [
        "http://www.66ip.cn/nmtq.php?getnum=500&isp=0&anonymoustype={0}&start=&ports=&export=&api=66ip".format(i)
        for i in range(3, 5)]

    def __init__(self):
        super().__init__()
        self._encoding = 'gbk'
        self._home_url = 'http://www.66ip.cn'

    def parse(self, html):
        lst = re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{2,5}', html)
        for it in lst:
            ip, port = it.split(':')
            if ip and port:
                self._proxies.append((ip, port))