import asyncio
import logging
import threading
import time
import requests
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
        self._encoding = 'utf-8'
        self._site_name = self.__class__.__name__
        self._urls = []
        self._base_url = None
        self._use_browser = False
        self._browser = None
        self._render_js = False
        self._session = None
        self._proxies = []

    @property
    def site_name(self):
        return self._site_name

    @property
    def proxies(self):
        return self._proxies

    def parse(self, html: HTML):
        raise NotImplementedError

    def parse_html(self, htext):
        raise NotImplementedError

    async def _async_page(self, url):
        page = await self._browser.newPage()
        # await page.setUserAgent("Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36")
        await page.goto(url, options={'timeout': int(8 * 1000)})
        await page.waitForNavigation({'waitUntil': 'load'})  # 66ip第一次访问会返回521，这里wait即可，或者再调用一次goto也行
        await self.async_parse_page(page)

    def get_html(self, url: str):
        resp = self._session.get(url, timeout=15)
        if resp and resp.ok and self._render_js:
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

    def reqs(self, url, header):
        logger.debug('crawling... %s', url)
        resp = requests.get(url, headers=header)
        resp.encoding = self._encoding
        self.parse_html(resp.text)
        resp.close()

    async def get_cookies(self):
        pages = await self._browser.pages()
        page = pages[0]
        ua = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'
        await page.setUserAgent(ua)
        logger.debug("open browser goto %s",self._base_url)
        await page.goto(self._base_url, options={'timeout': int(30 * 1000)})
        await page.waitForNavigation({'timeout': 1000 * 30})
        cookies = await page.cookies()
        lst = []
        for ck in cookies:
            lst.append('{}={}'.format(ck['name'], ck['value']))
        cookie = ';'.join(lst)
        # logger.info(await page.content())
        await page.close()
        headers = {
            'User-Agent': ua,
            'Cookie': cookie
        }
        return headers

    def callback(self, future):
        header = future.result()
        logger.info('callback:%s', header)
        for u in self._urls:
            self.reqs(u, header)
            logger.debug('{} crawl proxies: {}'.format(u, len(self._proxies)))
            time.sleep(self._sleep)

        # executor = ThreadPoolExecutor(max_workers=300)
        # tasks = [executor.submit(self.reqs, u, header) for u in self._urls]
        # concurrent.futures._base.wait(tasks, return_when=concurrent.futures._base.ALL_COMPLETED)
        # executor.shutdown()

    def craw_by_browser(self):
        if 'MainThread' != threading.current_thread().name:
            asyncio.set_event_loop(asyncio.new_event_loop())
        loop = asyncio.get_event_loop()
        self._browser = loop.run_until_complete(launch(headless=True, handleSIGINT=False,
                                                       handleSIGTERM=False, handleSIGHUP=False,
                                                       args=['--no-sandbox']))
        task = asyncio.ensure_future(self.get_cookies())
        task.add_done_callback(self.callback)
        asyncio.get_event_loop().run_until_complete(task)
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
