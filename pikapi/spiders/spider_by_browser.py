import logging

from lxml import etree
from pyquery import PyQuery
from pikapi.spiders.spider import BrowserSpider

logger = logging.getLogger(__name__)


class SpiderCoolProxy(BrowserSpider):
    name = 'www.cool-proxy.net'
    start_urls = [
            'https://www.cool-proxy.net/proxies/http_proxy_list/country_code:/port:/anonymous:1',
            'https://www.cool-proxy.net/proxies/http_proxy_list/country_code:/port:/anonymous:1/page:2',
            'https://www.cool-proxy.net/proxies/http_proxy_list/country_code:/port:/anonymous:1/page:3'
        ]
    parse_args = ('#main > table > tbody > tr', 'td', 0, 1)

    def __init__(self):
        super().__init__()
        self._req_timeout = 30

    async def browse(self, url):
        async with self._semaphore:
            page = await self._browser.newPage()
            await page.setUserAgent(self._ua)
            logger.debug("open page goto %s", url)
            await page.goto(url, options={'timeout': self._req_timeout*1000})
            # await page.waitForNavigation({'timeout': self._req_timeout*1000})
            await page.waitForSelector("#main > table > tbody > tr")
            html = await page.content()
            await page.close()
            return html


class SpiderGoubanjia(BrowserSpider):
    name = 'www.goubanjia.com'
    start_urls = ['http://www.goubanjia.com/']

    def parse(self, html):
        #直接请求返回的端口是不对的，所以改用浏览器请求
        # doc = PyQuery(html)
        # trs = doc('tr.success, .warning')
        # for t in trs.items():
        #     ip = t('td').eq(0)
        h = etree.HTML(html)
        trs = h.xpath('//table/tbody/tr')
        for tb in trs:
            ss = tb.xpath('td[@class="ip"]/*[not(@style="display: none;" or @style="display:none;")]/text()')
            ip = ''.join(ss[0:-1])
            port = ss[-1]
            self._proxies.append((ip, port))


class _SpiderProxydb(BrowserSpider):
    #载入超时
    name = 'proxydb.net'
    start_urls = ["http://proxydb.net/?protocol=http&protocol=https"]

    def parse(self, html):
        doc = PyQuery(html)
        trs = doc('.table > tbody:nth-child(2) > tr')
        for t in trs.items():
            ip = t('td').eq(0)
            print(ip)
            # if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', ip):
            #     self._proxies.append((ip, port))