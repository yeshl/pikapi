import requests
import json
import time
from pikapi.database import ProxyIP
from pikapi.loggings import logger
from pikapi.validators.base_validator import BaseValidator


class IpifyValidator(BaseValidator):
    def __init__(self, proxy_ip: ProxyIP, eip: str):
        super().__init__(proxy_ip, eip)
        self._http_check_url = 'http://api.ipify.org/?format=json'
        self._https_check_url = 'https://api.ipify.org/?format=json'

    def parse_ip(self, txt: str):
        j = json.loads(txt)
        return j['ip'] if j else ''

