import math
import time
import logging
import requests
import json
from pikapi.database import ProxyIP
from .tcpping import ping
from pikapi.loggings import logger

IP_CHECKER_API = 'http://api.ipify.org/?format=json'
IP_CHECKER_API_SSL = 'https://api.ipify.org/?format=json'
IP_INFO_AIP = 'http://ip-api.com/json/{0}?lang=zh-CN'
logging.captureWarnings(True)


class BaseValidator(object):
    def __init__(self, proxy_ip: ProxyIP, eip: str):
        self._proxy_ip = proxy_ip
        self._external_ip = eip
        self._http_check_url = IP_CHECKER_API
        self._https_check_url = IP_CHECKER_API_SSL
        self._latency, self._success_rate = math.inf, 0.0
        self._proxy = {
            'http': 'http://{}:{}'.format(self._proxy_ip.ip, self._proxy_ip.port),
            'https': 'https://{}:{}'.format(self._proxy_ip.ip, self._proxy_ip.port)
        }
        self._header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36',
            'Connection': 'keep-alive'}

    def ip_info(self):
        try:
            logger.debug("query ip info: {0} ".format(IP_INFO_AIP.format(self._proxy_ip.ip)))
            r = requests.get(IP_INFO_AIP.format(self._proxy_ip.ip), headers=self._header, verify=False, timeout=10)
            '''
            {"as":"AS14061 DigitalOcean, LLC","city":"North Bergen","country":"美国","countryCode":"US",
            "isp":"DigitalOcean, LLC","lat":40.8054,"lon":-74.0241,"org":"Digital Ocean","query":"159.203.186.40",
            "region":"NJ","regionName":"新泽西州","status":"success","timezone":"America/New_York","zip":"07047"}
            '''
            if r.ok:
                jtxt = json.loads(r.text)
                if jtxt:
                    self._proxy_ip.country = jtxt['country']
                    self._proxy_ip.country_code = jtxt['countryCode']
                    self._proxy_ip.region_name = jtxt['regionName']
                    self._proxy_ip.region = jtxt['region']
                    self._proxy_ip.city = jtxt['city']

        # except requests.RequestException as e:
        except Exception as e:
            logger.debug("query ip info Exception:{2}".format(self._proxy_ip.ip, e.__str__()))

    def validate_latency(self):
        try:
            (self._latency, self._success_rate) = ping(self._proxy_ip.ip, self._proxy_ip.port)
        except ConnectionRefusedError:
            self._latency, self._success_rate = math.inf, 0.0

    def validate_http(self):
        try:
            logger.debug("{0} -x {1}".format(self._http_check_url, self._proxy['http']))
            r = requests.get(self._http_check_url, proxies=self._proxy, headers=self._header, verify=False, timeout=10)
            if r.ok:
                ip = self.parse_ip(r.text)
                self._proxy_ip.http_pass_proxy_ip = ip
                self._proxy_ip.http_weight += 1
                if ip != self._external_ip:
                    self._proxy_ip.http_anonymous += 1
        # except requests.RequestException as e:
        except Exception as e:
            logger.debug("{0} -x {1} Exception:{2}".format(self._http_check_url, self._proxy['http'], e.__str__()))

    def validate_https(self):
        try:
            logger.debug("{0} -x {1}".format(self._https_check_url, self._proxy['https']))
            r = requests.get(self._https_check_url, proxies=self._proxy, headers=self._header, verify=False, timeout=10)
            if r.ok:
                ip = self.parse_ip(r.text)
                self._proxy_ip.https_pass_proxy_ip = ip
                self._proxy_ip.https_weight += 1
                if ip != self._external_ip:
                    self._proxy_ip.https_anonymous += 1
        # except requests.RequestException as e:
        except Exception as e:
            logger.debug("{0} -x {1} Exception:{2}".format(self._https_check_url, self._proxy['https'], e.__str__()))

    def parse_ip(self, txt: str):
        return txt

    def validate(self, times: int = 2):
        for i in range(times):
            time.sleep(0.5)
            self.validate_http()
            time.sleep(0.5)
            self.validate_https()

        if self._proxy_ip.country is None:
            self.ip_info()