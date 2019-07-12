from requests_html import HTML

from pikapi.database import ProxyIP
from .base_provider import BaseProvider


class IpaddressProvider(BaseProvider):
    def __init__(self):
        super().__init__()
        self._site_name = 'www.ipaddress.com'
        self._urls = [
            'https://www.ipaddress.com/proxy-list/'
        ]

    def parse(self, html: HTML):

        for ip_row in html.find('.proxylist tbody tr'):
            ip_port = ip_row.find('td:nth-child(1)', first=True).text
            ip, port = ip_port.split(":")
            if ip and port:
                self._proxies.append((ip, port))

