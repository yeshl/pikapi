import logging
from pyquery import PyQuery
from pikapi.spiders.spider import  BrowserSpider

logger = logging.getLogger(__name__)


class SpiderCoolProxy(BrowserSpider):
    name = 'www.cool-proxy.net'
    start_urls = [
            'https://www.cool-proxy.net/proxies/http_proxy_list/country_code:/port:/anonymous:1',
            'https://www.cool-proxy.net/proxies/http_proxy_list/country_code:/port:/anonymous:1/page:2',
            'https://www.cool-proxy.net/proxies/http_proxy_list/country_code:/port:/anonymous:1/page:3'
        ]

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

    def parse(self, html):
        doc = PyQuery(html)
        info = doc("#main > table > tbody > tr")
        for tr in info.items():
            ip = tr("td:first-child").text()
            port = tr("td").eq(1).text()
            self._proxies.append((ip, port))
