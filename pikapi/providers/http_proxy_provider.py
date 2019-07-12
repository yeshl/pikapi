import re

from requests_html import HTML

from pikapi.database import ProxyIP
from .base_provider import BaseProvider


class HttpProxyProvider(BaseProvider):
    def __init__(self):
        super().__init__()
        self._site_name = 'proxyhttp.net'
        self._render_js = True
        self._urls = [
            'https://proxyhttp.net/free-list/proxy-anonymous-hide-ip-address/',
            'https://proxyhttp.net/',
            'https://proxyhttp.net/free-list/anonymous-server-hide-ip-address/2#proxylist'
        ]

    def parse(self, html: HTML) -> [ProxyIP]:
        for ip_row in html.find('table.proxytbl tr'):
            ip_element = ip_row.find('td:nth-child(1)', first=True)
            port_element = ip_row.find('td:nth-child(2)', first=True)

            try:
                if ip_element and port_element:
                    port_str = re.search(r'//]]> (\d+)', port_element.text).group(1)
                    ip = ip_element.text
                    port = port_str
                    if ip and port:
                        self._proxies.append((ip, port))
            except AttributeError:
                pass

