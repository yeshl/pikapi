
import asyncio
import logging
import random
import re
import threading
import time
import requests
from pyppeteer import launch
from pyquery import PyQuery

logger = logging.getLogger(__name__)

USER_AGENT = [
    "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50",
    "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50",
    "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:38.0) Gecko/20100101 Firefox/38.0",
    "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; .NET4.0C; .NET4.0E; .NET CLR 2.0.50727; .NET CLR 3.0.30729; .NET CLR 3.5.30729; InfoPath.3; rv:11.0) like Gecko",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)",
    "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0)",
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:2.0.1) Gecko/20100101 Firefox/4.0.1",
    "Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1",
    "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; en) Presto/2.8.131 Version/11.11",
    "Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Maxthon 2.0)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; TencentTraveler 4.0)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; The World)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SE 2.X MetaSr 1.0; SE 2.X MetaSr 1.0; .NET CLR 2.0.50727; SE 2.X MetaSr 1.0)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; 360SE)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Avant Browser)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)",
    "Mozilla/5.0 (iPhone; U; CPU iPhone OS 4_3_3 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8J2 Safari/6533.18.5",
    "Mozilla/5.0 (iPod; U; CPU iPhone OS 4_3_3 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8J2 Safari/6533.18.5",
    "Mozilla/5.0 (iPad; U; CPU OS 4_3_3 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8J2 Safari/6533.18.5",
    "Mozilla/5.0 (Linux; U; Android 2.3.7; en-us; Nexus One Build/FRF91) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1",
    "MQQBrowser/26 Mozilla/5.0 (Linux; U; Android 2.3.7; zh-cn; MB200 Build/GRJ22; CyanogenMod-7) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1",
    "Opera/9.80 (Android 2.3.4; Linux; Opera Mobi/build-1107180945; U; en-GB) Presto/2.8.149 Version/11.10",
    "Mozilla/5.0 (Linux; U; Android 3.0; en-us; Xoom Build/HRI39) AppleWebKit/534.13 (KHTML, like Gecko) Version/4.0 Safari/534.13",
    "Mozilla/5.0 (BlackBerry; U; BlackBerry 9800; en) AppleWebKit/534.1+ (KHTML, like Gecko) Version/6.0.0.337 Mobile Safari/534.1+",
    "Mozilla/5.0 (hp-tablet; Linux; hpwOS/3.0.0; U; en-US) AppleWebKit/534.6 (KHTML, like Gecko) wOSBrowser/233.70 Safari/534.6 TouchPad/1.0",
    "Mozilla/5.0 (SymbianOS/9.4; Series60/5.0 NokiaN97-1/20.0.019; Profile/MIDP-2.1 Configuration/CLDC-1.1) AppleWebKit/525 (KHTML, like Gecko) BrowserNG/7.1.18124",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows Phone OS 7.5; Trident/5.0; IEMobile/9.0; HTC; Titan)",
    "UCWEB7.0.2.37/28/999",
    "NOKIA5700/ UCWEB7.0.2.37/28/999",
    "Openwave/ UCWEB7.0.2.37/28/999",
    "Mozilla/4.0 (compatible; MSIE 6.0; ) Opera/UCWEB7.0.2.37/28/999",
]


class Spider(object):
    name = 'Spider'
    domain = 'yeshl.com'
    start_urls = []
    parse_args = ('table > tbody > tr', 'td', 0, 1)

    def __init__(self):
        # self._ua = UserAgent().random
        self._ua = random.choice(USER_AGENT)
        self._headers = {'Connection': 'close', 'User-Agent': self._ua}
        self._encoding = 'utf-8'
        # self._site_name = self.__class__.__name__
        self._req_timeout = 30
        self._sleep = 1
        self._session = None
        self._crawproxy = {
            # 'http': 'http://{}:{}'.format(self._proxy_ip.ip, self._proxy_ip.port),
            # 'https': 'https://{}:{}'.format(self._proxy_ip.ip, self._proxy_ip.port)
        }
        self._proxies = []

    @property
    def proxies(self):
        return self._proxies

    def setUp(self):
        logger.info("%s crawl setUp" % self.name)

    def parse(self, html):
        doc = PyQuery(html)
        trs = doc(self.parse_args[0])
        for t in trs.items():
            ip = t(self.parse_args[1]).eq(self.parse_args[2]).text()
            if self.parse_args[3] > 0:
                port = t(self.parse_args[1]).eq(self.parse_args[3]).text()
            else:
                ips = ip.split(':')
                ip = ips[0]
                port = ips[1]
            if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', ip):
                self._proxies.append((ip, port))

    def reqs(self, url):
        logger.info('reqs {}'.format(url))
        resp = requests.get(url, headers=self._headers, proxies=self._crawproxy,
                            timeout=(10, self._req_timeout), verify=False)
        resp.encoding = self._encoding
        resp.close()
        return resp.text

    def crawl(self):
        exc = None
        self._session = requests.session()
        try:
            logger.info('{} crawl BEGIN'.format(self.name))
            self.setUp()
            for url in self.start_urls:
                logger.info('requests {}'.format(url))
                try:
                    resp = self._session.get(url, headers=self._headers,  proxies=self._crawproxy,
                                             timeout=(15, self._req_timeout), verify=False)
                except Exception as e1:
                    if self.name == 'txt':
                        logger.error("{} :{}".format(url, e1))
                        continue
                    else:
                        raise e1
                resp.encoding = self._encoding
                if resp.status_code == 200:
                    self.parse(resp.text)
                    logger.info('{} crawl proxies: {}'.format(url, len(self._proxies)))
                else:
                    logger.error("response code：{} from {}".format(resp.status_code, url))
                time.sleep(self._sleep)
        except Exception as e:
            logger.error("error:%s", str(e), exc_info=True)
            exc = e
        finally:
            self._session.close()
        return self, exc

    def __str__(self):
        return self.name


class CookieSpider(Spider):
    name = 'CookieSpider'

    def __init__(self):
        super().__init__()
        self._browser = None
        self._home_url = None
        self._req_timeout = 30

    async def browse(self, url):
        pages = await self._browser.pages()
        page = pages[0]
        await page.setUserAgent(self._ua)
        logger.debug("open browser goto %s", url)
        await page.goto(url, options={'timeout': self._req_timeout*1000})
        await page.waitForNavigation({'timeout': self._req_timeout*1000})
        # await page.goto(url, options={'timeout': self._req_timeout}) #goto again for www.66ip.cn
        cookies = await page.cookies()
        lst = []
        for ck in cookies:
            lst.append('{}={}'.format(ck['name'], ck['value']))
        cookie = ';'.join(lst)
        await page.close()
        headers = {
            'User-Agent': self._ua,
            'Cookie': cookie
        }
        return headers

    def callback(self, future):
        header = future.result()
        logger.debug('browser headers(cookies) :%s', header)
        self._headers = header

    def setUp(self):
        super().setUp()
        if 'MainThread' != threading.current_thread().name:
            asyncio.set_event_loop(asyncio.new_event_loop())
        loop = asyncio.get_event_loop()
        try:
            self._browser = loop.run_until_complete(launch(headless=True, handleSIGINT=False,
                                                           handleSIGTERM=False, handleSIGHUP=False,
                                                           args=['--no-sandbox']
                                                           ))

            task = asyncio.ensure_future(self.browse(self._home_url))
            # task.add_done_callback(self.callback)

            asyncio.get_event_loop().run_until_complete(task)
        except Exception as e:
            logger.error("asyncio error:%s", str(e), exc_info=True)
            raise e
        finally:
            try:
                logger.info('chromium closing')
                loop.run_until_complete(self._browser.close())
                self._browser.process.communicate()#close FIFO pipe
                logger.info('chromium closed')
            finally:
                loop.close()#close socket
                logger.info('loop closed ')


class BrowserSpider(Spider):
    name = 'BrowserSpider'

    def __init__(self):
        super().__init__()
        self._semaphore = None
        self._browser = None
        self._req_timeout = 45

    async def browse(self, url):
        async with self._semaphore:
            page = await self._browser.newPage()
            await page.setUserAgent(self._ua)
            logger.debug("open page goto %s", url)
            await page.goto(url, options={'timeout': self._req_timeout*1000})
            # await page.waitForNavigation({'timeout': self._req_timeout*1000})
            # await page.goto(url, options={'timeout': self._req_timeout*1000}) #goto again for www.66ip.cn
            html = await page.content()
            await page.close()
            return html

    def callback(self, future):
        try:
            html = future.result()
            self.parse(html)
        except Exception as ex:
            logger.error("callback error:%s", str(ex), exc_info=True)

    def crawl_by_browser(self):

        if 'MainThread' != threading.current_thread().name:
            asyncio.set_event_loop(asyncio.new_event_loop())
        loop = asyncio.get_event_loop()
        try:
            self._semaphore = asyncio.Semaphore(5)
            self._browser = loop.run_until_complete(launch(headless=True, handleSIGINT=False,
                                                           handleSIGTERM=False, handleSIGHUP=False,
                                                           args=['--no-sandbox']
                                                           ))
            tasks = [asyncio.ensure_future(self.browse(url)) for url in self.start_urls]
            # for t in tasks:
            #     t.add_done_callback(self.callback)
            rst = loop.run_until_complete(asyncio.gather(*tasks))
        except Exception as e:
            logger.error("asyncio error:%s", str(e), exc_info=True)
            raise e
        finally:
            try:
                logger.info('chromium closing')
                loop.run_until_complete(self._browser.close())
                self._browser.process.communicate()#close FIFO pipe
                logger.info('chromium closed')
            finally:
                loop.close()#close socket
                logger.info('loop closed ')

    def crawl(self):
        self.setUp()
        exc = None
        try:
            self.crawl_by_browser()
        except Exception as e:
            logger.error("crawl_by_browser error:%s", str(e), exc_info=True)
            exc = e
        return self, exc
