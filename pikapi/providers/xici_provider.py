from requests_html import HTML

from pikapi.providers import BaseProvider


class XiciProvider(BaseProvider):
    def __init__(self):
        super().__init__()
        self._site_name = 'xicidaili'
        self._urls = ['http://www.xicidaili.com/{}/{}'.format(c, i) for c in ['nn', 'wn', 'wt'] for i in range(1, 4)]

    def parse(self, html: HTML):
        for ip_row in html.find('#ip_list tr'):
            ip_element = ip_row.find('td:nth-child(2)', first=True)
            port_element = ip_row.find('td:nth-child(3)', first=True)
            if ip_element and port_element:
                ip = ip_element.text
                port = port_element.text
                if ip and port:
                    self._proxies.append((ip, port))
