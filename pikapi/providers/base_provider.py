import asyncio
import logging
import time
import traceback

from pyppeteer import launch
from requests_html import HTML
from requests_html import HTMLSession
from fake_useragent import UserAgent

logger = logging.getLogger(__name__)


class BaseProvider(object):
    def __init__(self):
        self._sleep = 1
        self._ua = UserAgent().random
        self._headers = {
            "User-Agent": self._ua
        }
        self._site_name = self.__class__.__name__
        self._urls = []
        self._browse_url = None
        self._render_js = False
        self._session = None
        self._browser = None
        self._proxies = []

    @property
    def site_name(self):
        return self._site_name

    def parse(self, html: HTML):
        raise NotImplementedError

    async def async_parse_page(self, page):
        raise NotImplementedError

    async def _async_page(self, url):
        page = await self._browser.newPage()
        # await page.setUserAgent("Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36")
        await page.goto(url, options={'timeout': int(8 * 1000)})
        await page.waitForNavigation({'waitUntil': 'load'})  # 66ip第一次访问会返回521，这里wait即可，或者再调用一次goto也行
        await self.async_parse_page(page)


    def get_html(self, url: str):
        resp = self._session.get(url, headers=self._headers, timeout=15)
        if resp.status_code == 521:
            cookies_1 = ';'.join(['='.join(item) for item in resp.cookies.items()])
            cookies_2 = self.exec_js(resp.text)
            cookies = "{0};{1}".format(cookies_1, cookies_2)
            self._headers["Cookie"] = cookies
            resp = self._session.get(url, headers=self._headers)
        elif resp and resp.ok and self._render_js:
            resp.html.render(wait=1.5, timeout=10.0)
        return resp.html if resp else None

    def craw_by_request(self):
        self._session = HTMLSession()
        try:
            for url in self._urls:
                logger.debug('crawl {}'.format(url))
                html = self.get_html(url)
                if html:
                    self.parse(html)
                    logger.debug('{} crawl proxies: {}'.format(url, len(self._proxies)))
                else:
                    logger.error("page not found! :{}".format(url))
                time.sleep(self._sleep)
        finally:
            self._session.close()

    def craw_by_browser(self):
        loop = asyncio.get_event_loop()
        self._browser = loop.run_until_complete(launch(headless=True, args=['--no-sandbox']))
        for url in self._urls:
            logger.debug('async crawl {}'.format(url))
            loop.run_until_complete(self._async_page(url))
            logger.debug('{} async crawl proxies: {}'.format(url, len(self._proxies)))
        loop.run_until_complete(self._browser.close())

    def crawl(self, validator_queue):
        exc = None
        try:
            if self._use_browser:
                self.craw_by_browser()
            else:
                self.craw_by_request()
        except Exception as e:
            exc = e
        return self, validator_queue, exc

    def __str__(self):
        return self._site_name
