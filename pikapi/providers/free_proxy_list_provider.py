from requests_html import HTML

from pikapi.database import ProxyIP
from .base_provider import BaseProvider


class FreeProxyListProvider(BaseProvider):
    def __init__(self):
        super().__init__()
        self._site_name = 'free-proxy-list.net'
        self._urls = [
            'https://free-proxy-list.net/'
        ]

    def parse(self, html: HTML) -> [ProxyIP]:
        for ip_row in html.find('#proxylisttable tbody tr'):
            ip = ip_row.find('td:nth-child(1)', first=True).text
            port = ip_row.find('td:nth-child(2)', first=True).text
            if ip and port:
                self._proxies.append((ip, port))
