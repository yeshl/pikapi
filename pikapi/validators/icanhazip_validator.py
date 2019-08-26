import logging
from pikapi.store import ProxyIP
from pikapi.validators.base_validator import BaseValidator

logger = logging.getLogger(__name__)


class IcanhazipValidator(BaseValidator):
    def __init__(self, proxy_ip: ProxyIP, eip: str):
        super().__init__(proxy_ip, eip)
        self._http_check_url = 'http://icanhazip.com/'
        self._https_check_url = 'https://icanhazip.com/'
