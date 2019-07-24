from pikapi.database import ProxyIP
from pikapi.validators.base_validator import BaseValidator


class YslValidator(BaseValidator):
    def __init__(self, proxy_ip: ProxyIP, eip: str):
        super().__init__(proxy_ip, eip)
        self._http_check_url = 'http://139.196.90.71:8044/ysl'
        self._https_check_url = 'https://139.196.90.71:8443/ysl'

    def parse_ip(self, txt: str):
        ip, port = eval(txt)
        return ip

