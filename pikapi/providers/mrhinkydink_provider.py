import re

from requests_html import HTML
from pikapi.providers.base_provider import BaseProvider


class MrhinkydinkProvider(BaseProvider):
    def __init__(self):
        super().__init__()
        self._site_name = 'www.mrhinkydink.com'
        # self._render_js = True
        self._urls = ['http://www.mrhinkydink.com/proxies.htm',
                      'http://www.mrhinkydink.com/proxies2.htm',
                      'http://www.mrhinkydink.com/proxies3.htm'
                      ]

    def parse(self, html: HTML):
        tabs = html.find('table')
        i = 0
        for tr in tabs[4].find('tr'):
            i += 1
            if i > 3:
                j = 0
                ip, port = None, None
                for td in tr.find('td'):
                    j += 1
                    if j == 1:
                        ip = td.text.replace('*', '')
                    elif j == 2:
                        port = td.text
                    else:
                        break
                if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', ip):
                    self._proxies.append((ip, port))
