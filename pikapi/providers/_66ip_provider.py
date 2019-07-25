import logging
import re

from lxml import etree
from requests_html import HTML
from pikapi.providers.base_provider import BaseProvider
logger = logging.getLogger(__name__)


class _66ipProvider(BaseProvider):
    def __init__(self):
        super().__init__()
        self._site_name = 'www.66ip.cn'
        # self._sleep = 2
        self._encoding = 'gbk'
        self._base_url = 'http://www.66ip.cn'
        # self._urls = ['http://www.66ip.cn/%s.html' % i for i in range(1, 3)] + \
        #              ['http://www.66ip.cn/areaindex_%s/%s.html' % (i, j) for i in range(1, 35) for j in range(1, 3)]
        self._urls = ['http://www.66ip.cn/%s.html' % i for i in range(1, 3)]
        self._use_browser = True

    def parse_html(self, htext):
        html = etree.HTML(htext)
        table = html.xpath('//table/tr[position()>1]')
        for r in table:
            ip = r.xpath(".//td[1]/text()")[0]
            port = r.xpath(".//td[2]/text()")[0]
            if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', ip):
                self._proxies.append((ip, port))

    def parse(self, html: HTML):
        tabs = html.find('table')
        for tr in tabs[2].find('tr'):
           ip = tr.find('td:nth-child(1)', first=True).text
           port = tr.find('td:nth-child(2)', first=True).text
           if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', ip):
               self._proxies.append((ip, port))

