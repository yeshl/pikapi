import re

from requests_html import HTML
from .base_provider import BaseProvider


class CoolProxyProvider(BaseProvider):
    def __init__(self):
        super().__init__()
        self._site_name = 'www.cool-proxy.net'
        self._render_js = True
        self._urls = [
            'https://www.cool-proxy.net/proxies/http_proxy_list/country_code:/port:/anonymous:1',
            'https://www.cool-proxy.net/proxies/http_proxy_list/country_code:/port:/anonymous:1/page:2',
            'https://www.cool-proxy.net/proxies/http_proxy_list/country_code:/port:/anonymous:1/page:3'
        ]

    def parse(self, html: HTML):
        for ip_row in html.find('table tr'):
            ip_element = ip_row.find('td:nth-child(1)', first=True)
            port_element = ip_row.find('td:nth-child(2)', first=True)

            if ip_element and port_element:
                ip = re.sub(r'document\.write\(.+\)', '', ip_element.text)
                port = port_element.text
                if ip and port:
                    self._proxies.append((ip, port))
