import datetime
import math
import logging

from peewee import CharField, DateTimeField, BooleanField, FloatField, IntegerField, SqliteDatabase
from playhouse.signals import pre_save, Model

from pikapi.config import get_config
from pikapi.loggings import logger

_db = None


# logger = logging.getLogger('peewee')
# logger.setLevel(logging.DEBUG)
# logger.addHandler(logging.StreamHandler())


def create_connection() -> SqliteDatabase:
    global _db
    if _db:
        return _db
    else:
        logger.debug('create new db connection')
        _db = SqliteDatabase(get_config('db_path', './pikapi.db'))
        return _db


def create_db_tables():
    db = create_connection()
    db.create_tables([ProxyIP, ProxyWebSite])


class BaseModel(Model):
    class Meta:
        database = create_connection()


class ProxyWebSite(BaseModel):
    class Meta:
        table_name = 'proxy_site'

    site_name = CharField(unique=True, max_length=128)
    proxy_count = IntegerField(default=0)
    last_fetch = DateTimeField(null=True)
    this_fetch = DateTimeField(default=datetime.datetime.now)
    stats = CharField(null=True)

    def merge(self):
        cnt = ProxyWebSite.update(proxy_count=self.proxy_count,
                                  last_fetch=ProxyWebSite.this_fetch,
                                  this_fetch=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
                                  stats=self.stats) \
            .where(ProxyWebSite.site_name == self.site_name).execute()
        if 0 == cnt:
            cnt = self.save()
        return cnt

    def __str__(self):
        return '[site_name: {}, proxy_count: {}, last_fetch: {}, this_fetch: {}, stats: {}]' \
            .format(self.site_name, self.proxy_count, self.last_fetch, self.this_fetch, self.stats)


class ProxyIP(BaseModel):
    class Meta:
        table_name = 'proxy_ips'

    ip = CharField(unique=True, max_length=16)
    port = IntegerField()
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)
    latency = FloatField()
    # stability = FloatField()
    http_pass_proxy_ip = CharField(null=True, max_length=16)
    https_pass_proxy_ip = CharField(null=True, max_length=16)
    http_anonymous = IntegerField(default=0)
    https_anonymous = IntegerField(default=0)
    http_weight = IntegerField(default=0)
    https_weight = IntegerField(default=0)
    country = CharField(null=True, max_length=32)
    country_code = CharField(null=True, max_length=10)
    region_name = CharField(null=True, max_length=32)
    region = CharField(null=True, max_length=32)
    city = CharField(null=True, max_length=32)

    def __str__(self):
        return 'ProxyIP{{ip: {}, port: {}, http_pass_proxy_ip: {}, https_pass_proxy_ip: {},' \
               ' http_anonymous: {}, https_anonymous: {}, http_weight: {}, https_weight: {}, https_weight: {}}}' \
            .format(self.ip, self.port, self.http_pass_proxy_ip, self.https_pass_proxy_ip,
                    self.http_anonymous, self.https_anonymous, self.http_weight, self.https_weight, self.country)

    def __repr__(self):
        return self.__str__()

    def merge(self):
        cnt = ProxyIP.update(http_pass_proxy_ip=self.http_pass_proxy_ip, https_pass_proxy_ip=self.https_pass_proxy_ip,
                             http_anonymous=self.http_anonymous, https_anonymous=self.https_anonymous,
                             http_weight=self.http_weight, https_weight=self.https_weight,
                             updated_at=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")) \
            .where(ProxyIP.ip == self.ip).execute()
        if 0 == cnt:
            cnt = self.save()
        return cnt


# @pre_save(sender=ProxyIP)
# def proxy_ip_on_pre_save_handler(model_class, instance: ProxyIP, created):
#     instance.latency = math.floor(instance.latency if instance.latency else -1)