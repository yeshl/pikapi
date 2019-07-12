from requests_html import HTML

from pikapi.database import ProxyIP
from pikapi.providers import BaseProvider


class Data5uProvider(BaseProvider):

    def __init__(self):
        super().__init__()
        self._site_name = 'www.data5u.com'
        self._urls = [
            'http://www.data5u.com/free/gwgn/index.shtml',
            'http://www.data5u.com/free/gngn/index.shtml'
        ]

    def parse(self, html: HTML):
        for ip_row in html.find('.wlist > ul > li:nth-child(2) .l2'):
            ip_element = ip_row.find('span:nth-child(1)', first=True)
            port_element = ip_row.find('span:nth-child(2)', first=True)

            if ip_element and port_element:
                ip = ip_element.text
                port = port_element.text
                if ip and port:
                    self._proxies.append((ip, port))
