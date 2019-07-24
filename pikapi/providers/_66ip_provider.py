import logging
import re

from requests_html import HTML
from pikapi.providers.base_provider import BaseProvider
logger = logging.getLogger(__name__)


class _66ipProvider(BaseProvider):
    def __init__(self):
        super().__init__()
        self._site_name = 'www.66ip.cn'
        # self._sleep = 2
        # self._urls = ['http://www.66ip.cn/%s.html' % i for i in range(1, 3)] + \
        #              ['http://www.66ip.cn/areaindex_%s/%s.html' % (i, j) for i in range(1, 35) for j in range(1, 3)]
        self._browse_url = 'http://www.66ip.cn'
        self._urls = ['http://www.66ip.cn/1.html']
        # self._headers["Host"] = "www.66ip.cn"

    async def async_parse_page(self, page):
        eles = await page.querySelectorAll('#main > div > div:nth-child(1) > table > tbody > tr')
        for it in eles:
            ip = await (await (await it.querySelector(':nth-child(1)')).getProperty('textContent')).jsonValue()
            port = await (await (await it.querySelector(':nth-child(2)')).getProperty('textContent')).jsonValue()
            if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', ip):
                self._proxies.append((ip, port))

    def parse(self, html: HTML):
        tabs = html.find('table')
        for tr in tabs[2].find('tr'):
           ip = tr.find('td:nth-child(1)', first=True).text
           port = tr.find('td:nth-child(2)', first=True).text
           if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', ip):
               self._proxies.append((ip, port))

