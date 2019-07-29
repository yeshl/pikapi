import json
import requests
from datetime import datetime, timedelta

from pikapi.applog import logger
from pikapi.database import ProxyIP
from pikapi.validators import all_validators

__EXTERNAL_IP__ = None


def get_current_ip():
    global __EXTERNAL_IP__
    if __EXTERNAL_IP__:
        return __EXTERNAL_IP__
    else:
        r = requests.get("http://api.ipify.org/?format=json")
        j = json.loads(r.text)
        __EXTERNAL_IP__ = j['ip']
        return __EXTERNAL_IP__


class ValidateManager(object):
    def __init__(self, proxy: ProxyIP):
        proxy.latency = -1
        proxy.http_weight = 0
        proxy.https_weight = 0
        proxy.http_anonymous = 0
        proxy.https_anonymous = 0
        proxy.http_pass_proxy_ip = None
        proxy.https_pass_proxy_ip = None
        self._proxy = proxy

    def validate(self):
        for vs in all_validators:
            validator = vs(self._proxy, get_current_ip())
            validator.validate(1)
            if self._proxy.http_weight+self._proxy.https_weight <= 0:
                break

        self.save()

    def save(self):
        logger.debug(self._proxy)
        self._proxy.merge()

    @classmethod
    def should_validate(cls, proxy_ip: ProxyIP) -> bool:
        if proxy_ip.id is None:
            for p in ProxyIP.select().where(ProxyIP.ip == proxy_ip.ip):
                if p.http_weight+proxy_ip.https_weight <= 0 \
                        and datetime.now() - p.updated_at < timedelta(hours=24*p.failed_validate):
                    return False
        return True
