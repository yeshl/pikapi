import datetime
import logging


logger = logging.getLogger(__name__)


G_PROXY_WEB = {}
G_PROXY_IP = {}


class BaseModel:
    store = None

    def __init__(self, key):
        self.key = key

    @classmethod
    def get(cls, name):
        return cls.store.get(name)

    @classmethod
    def save(cls, inst):
        cls.store[inst.key] = inst

    @classmethod
    def delete(cls, name):
        return cls.store.pop(name, None)

    @classmethod
    def select(cls, fn):
        return list(filter(fn, list(cls.store.values())))


class ProxyWebSite(BaseModel):
    store = G_PROXY_WEB
    # table_name = 'proxy_site'

    def __init__(self, **kwargs):
        self.__site_name = kwargs.get('site_name')
        self.__proxy_count = kwargs.get('proxy_count', 0)
        self.__last_fetch = kwargs.get('last_fetch')
        self.__this_fetch = kwargs.get('this_fetch', datetime.datetime.now())
        self.__stats = kwargs.get('stats', 'OK')
        super().__init__(self.__site_name)

    def save(self):
        old = self.get(self.site_name)
        if old is not None:
            self.__last_fetch = old.__this_fetch
        super().save(self)

    def delete_self(self):
        super().delete(self.key)

    @property
    def site_name(self):
        return self.__site_name

    @site_name.setter
    def site_name(self, value):
        self.__site_name = value

    @property
    def proxy_count(self):
        return self.__proxy_count

    @proxy_count.setter
    def proxy_count(self, value):
        self.__proxy_count = value

    @property
    def last_fetch(self):
        return self.__last_fetch

    @last_fetch.setter
    def last_fetch(self, value):
        self.__last_fetch = value

    @property
    def this_fetch(self):
        return self.__this_fetch

    @this_fetch.setter
    def this_fetch(self, value):
        self.__this_fetch = value

    @property
    def stats(self):
        return self.__stats

    @stats.setter
    def stats(self, value):
        self.__stats = value

    def __str__(self):
        return '<site_name: {}, proxy_count: {}, last_fetch: {}, this_fetch: {}, stats: {}>' \
            .format(self.site_name, self.proxy_count, self.last_fetch, self.this_fetch, self.stats)

    def __repr__(self):
        return self.__str__()


class ProxyIP(BaseModel):
    store = G_PROXY_IP
    # table_name = 'proxy_ip'

    def __init__(self, **kwargs):
        self.ip = kwargs.get('ip')
        self.port = kwargs.get('port')
        self.created_at = kwargs.get('created_at', datetime.datetime.now())
        self.updated_at = kwargs.get('updated_at')
        self.latency = kwargs.get('latency', -1)
        self.google = kwargs.get('google', 0)
        self.failed_validate = kwargs.get('failed_validate', 0)
        self.http_pass_proxy_ip = kwargs.get('http_pass_proxy_ip')
        self.https_pass_proxy_ip = kwargs.get('https_pass_proxy_ip')
        self.http_anonymous = kwargs.get('http_anonymous', 0)
        self.https_anonymous = kwargs.get('https_anonymous', 0)
        self.http_weight = kwargs.get('http_weight', 0)
        self.https_weight = kwargs.get('https_weight', 0)
        self.country = kwargs.get('country')
        self.country_code = kwargs.get('country_code')
        self.region_name = kwargs.get('region_name')
        self.region = kwargs.get('region')
        self.city = kwargs.get('city')
        super().__init__(self.ip)

    def save(self):
        self.updated_at = datetime.datetime.now()
        if self.http_weight + self.https_weight <= 0:
            self.failed_validate = self.failed_validate + 1
        super().save(self)

    def delete_self(self):
        super().delete(self.key)

    def __str__(self):
        # return '{}:{}'.format(self.ip, self.port)
        return '<ip: {}, port: {}, ' \
               ' updated_at: {}, http_weight: {}, https_weight: {}>\n' \
            .format(self.ip, self.port,
                    self.updated_at, self.http_weight, self.https_weight)

    def __repr__(self):
        return self.__str__()
