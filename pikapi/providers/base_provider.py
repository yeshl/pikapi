import time
import traceback
from requests_html import HTML
from requests_html import HTMLSession
from pikapi.loggings import logger


class BaseProvider(object):

    def __init__(self):
        self._sleep = 1
        self._site_name = self.__class__.__name__
        self._urls = []
        self._render_js = False
        self._session = None
        self._proxies = []

    @property
    def site_name(self):
        return self._site_name

    def parse(self, html: HTML):
        raise NotImplementedError

    def get_html(self, url: str):
        resp = self._session.get(url, timeout=15)
        if resp and resp.ok and self._render_js:
            resp.html.render(wait=1.5, timeout=10.0)
        return resp.html if resp else None

    def crawl(self):
        self._session = HTMLSession()
        try:
            for url in self._urls:
                logger.debug('crawl {}'.format(url))
                html = self.get_html(url)
                if html:
                    self.parse(html)
                else:
                    logger.error("page not found! :{}".format(url))
                time.sleep(self._sleep)
        finally:
            self._session.close()

        return self._proxies

    def __str__(self):
        return self._site_name
