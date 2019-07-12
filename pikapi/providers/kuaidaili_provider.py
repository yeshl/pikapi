from requests_html import HTML

from pikapi.database import ProxyIP
from pikapi.providers import BaseProvider


class KuaidailiProvider(BaseProvider):
    def __init__(self):
        super().__init__()
        self._site_name = 'www.kuaidaili.com'
        self._render_js = True
        self._urls = [
            'https://www.kuaidaili.com/free/',
            'https://www.kuaidaili.com/free/inha/2/',
            'https://www.kuaidaili.com/free/inha/3/'
        ]

    def parse(self, html: HTML) -> [ProxyIP]:
        ip_list: [ProxyIP] = []

        for ip_row in html.find('#list table tr'):

            ip_element = ip_row.find('td[data-title="IP"]', first=True)
            port_element = ip_row.find('td[data-title="PORT"]', first=True)

            if ip_element and port_element:
                ip=ip_element.text
                port=port_element.text
                if ip and port:
                    self._proxies.append((ip, port))

