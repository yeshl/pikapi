import json
import re
import time

import requests
from datetime import datetime, timedelta

from pikapi.applog import logger
from pikapi.database import ProxyIP, _db
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
        proxy.google = 0
        proxy.http_weight = 0
        proxy.https_weight = 0
        proxy.http_anonymous = 0
        proxy.https_anonymous = 0
        proxy.http_pass_proxy_ip = None
        proxy.https_pass_proxy_ip = None
        self._proxy = proxy

    def validate_google(self):
        proxies = {'https': 'https://{}:{}'.format(self._proxy.ip, self._proxy.port)}
        try:
            r = requests.get('https://www.google.com',
                             proxies=proxies,
                             headers={
                                 'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36',
                                 'Connection': 'keep-alive'},
                             verify=False,
                             timeout=(5, 10))
            if r.ok:
                gp = re.search(r'<title>.*</title>', r.text, re.IGNORECASE)
                if gp[0].count('Google') == 1:
                    self._proxy.google += 1
        except Exception as e:
            logger.debug("{0} -x {1} Exception:{2}".format('https://www.google.com', proxies['https'], e.__str__()))

    def validate(self):
        c0 = time.perf_counter()
        logger.debug("validate BEGIN {}".format(self._proxy))
        for vs in all_validators:
            validator = vs(self._proxy, get_current_ip())
            validator.validate(1)
            if self._proxy.http_weight+self._proxy.https_weight <= 0:
                break
        self._proxy.latency = round(time.perf_counter() - c0, 2)
        if self._proxy.https_weight > 0:
            self.validate_google()
        logger.debug("validate END {} weight:{} elapsed:{}s".format(self._proxy,
                                             self._proxy.http_weight + self._proxy.https_weight,
                                             self._proxy.latency))
        self.save()

    def save(self):
        self._proxy.merge()

    @classmethod
    def should_validate(cls, proxy_ip: ProxyIP) -> bool:
        if proxy_ip.id is None:
            with _db.connection_context():
                p = ProxyIP.get_or_none(ProxyIP.ip == proxy_ip.ip)
            if p is not None:
                if p.updated_at > datetime.now() - timedelta(minutes=20):
                    return False
                if p.latency > 40 and p.updated_at > datetime.now() - timedelta(hours=12):
                    return False
                if p.http_weight+p.https_weight <= 0 and p.updated_at > datetime.now() - timedelta(hours=12):
                    return False
        return True
