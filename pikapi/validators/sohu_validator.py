import requests
import json
import time
from pikapi.database import ProxyIP
from pikapi.loggings import logger
from pikapi.validators.base_validator import BaseValidator


class SohuValidator(BaseValidator):
    def __init__(self, proxy_ip: ProxyIP, eip: str):
        super().__init__(proxy_ip, eip)
        self._http_check_url = 'http://pv.sohu.com/cityjson'
        self._https_check_url = 'https://pv.sohu.com/cityjson'

    def parse_ip(self, txt: str):
        arr = txt.split('=')
        if arr and len(arr) == 2:
            j = json.loads(arr[1].rstrip(';'))
        return j['cip'] if j else ''
