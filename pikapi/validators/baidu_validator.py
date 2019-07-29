from pikapi.database import ProxyIP
from pikapi.validators.base_validator import BaseValidator


class BaiduValidator(BaseValidator):
    def __init__(self, proxy_ip: ProxyIP, eip: str):
        super().__init__(proxy_ip, eip)
        self._http_check_url = 'http://www.baidu.com'
        self._https_check_url = 'https://www.baidu.com'

    def parse_ip(self, txt: str):
        return ''

