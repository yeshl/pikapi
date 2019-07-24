import re

from requests_html import HTML
from pikapi.providers import BaseProvider


class SpysOneProvider(BaseProvider):
    def __init__(self):
        super().__init__()
        self._site_name = 'spys.one'
        self._render_js = True
        self._urls = [
            'http://spys.one/en/anonymous-proxy-list/',
            # 'http://spys.one/en/http-proxy-list/',
            # 'http://spys.one/en/https-ssl-proxy/',
        ]

    def parse(self, html: HTML):
        for ip_row in html.find('table tr[onmouseover]'):
            ip_port_text_elem = ip_row.find('.spy14', first=True)
            if ip_port_text_elem:
                ip_port_text = ip_port_text_elem.text
                ip = re.search(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', ip_port_text).group(0)
                port = re.search(r':\n(\d{2,5})', ip_port_text).group(1)
                if ip and port:
                    self._proxies.append((ip, port))
