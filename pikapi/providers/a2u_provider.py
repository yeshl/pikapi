import re
from requests_html import HTML
from .base_provider import BaseProvider


class A2uProvider(BaseProvider):
    def __init__(self):
        super().__init__()
        self._site_name = 'githubusercontent.com/a2u'
        self._urls = ['https://raw.githubusercontent.com/a2u/free-proxy-list/master/free-proxy-list.txt']

    def parse(self, html: HTML):
        text = html.raw_html
        ip_port_str_list = re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{2,5}', text.decode('utf-8'))
        for ip_port in ip_port_str_list:
            ip = re.search(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', ip_port).group(0)
            port = re.search(r':(\d{2,5})', ip_port).group(1)

            if ip and port:
                self._proxies.append((ip, port))

