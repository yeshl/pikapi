import datetime
import logging

from peewee import CharField, DateTimeField, FloatField, IntegerField, SqliteDatabase, MySQLDatabase
from playhouse.db_url import connect
from playhouse.signals import Model
from playhouse.sqliteq import SqliteQueueDatabase

from pikapi.config import get_config

logger = logging.getLogger(__name__)

# logger = logging.getLogger('peewee')
# logger.setLevel(logging.DEBUG)
# logger.addHandler(logging.StreamHandler())

db_path = get_config('db_path', './pikapi.db')
logger.info('create new db1 connection %s', db_path)
# _db = SqliteQueueDatabase(
#     db_path,
#     use_gevent=False,
#     autostart=True,
#     queue_max_size=256,  # Max. # of pending writes that can accumulate.
#     results_timeout=10.0)  # Max. time to wait for query to be executed.

# _db = connect('mysql+pool://admin:123456@localhost:3306/db1?max_connections=50&stale_timeout=300&timeout=0')

_db = connect('sqlite+pool:///'+db_path+'?max_connections=50&stale_timeout=300&timeout=0&check_same_thread=False')
_db.journal_mode = 'wal'


for k in dir(_db):
    if not k.startswith('_'):
        o = getattr(_db, k)
        if type(o) in [tuple, list, str, int, bool]:
            logger.info("{}={}".format(k, str(o)))


class BaseModel(Model):
    class Meta:
        database = _db


class ProxyWebSite(BaseModel):
    class Meta:
        table_name = 'proxy_site'

    site_name = CharField(unique=True, max_length=128)
    proxy_count = IntegerField(default=0)
    last_fetch = DateTimeField(null=True)
    this_fetch = DateTimeField(default=datetime.datetime.now)
    stats = CharField(null=True)

    def merge(self):
        logger.info('update crawl BEGIN %s' % str((self.site_name, self.proxy_count, self.stats)))
        with _db.connection_context():
            cnt = ProxyWebSite.update(proxy_count=self.proxy_count,
                                  last_fetch=ProxyWebSite.this_fetch,
                                  this_fetch=datetime.datetime.now(),
                                  stats=self.stats) \
             .where(ProxyWebSite.site_name == self.site_name).execute()
            # cnt=0
            logger.info('update crawl END %s' % str((self.site_name, self.proxy_count, self.stats)))
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
    updated_at = DateTimeField(null=True, default=datetime.datetime.now)
    latency = FloatField(default=-1)
    google = IntegerField(default=0)
    failed_validate = IntegerField(default=0)
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
        return '{}:{}'.format(self.ip, self.port)
        # return 'ProxyIP{{ip: {}, port: {}, ' \
        #        ' http_anonymous: {}, https_anonymous: {}, http_weight: {}, https_weight: {}, country: {}}}' \
        #     .format(self.ip, self.port,
        #             self.http_anonymous, self.https_anonymous, self.http_weight, self.https_weight, self.country)

    def __repr__(self):
        return self.__str__()

    def merge(self):
        if self.http_weight + self.https_weight <= 0:
            self.failed_validate = self.failed_validate + 1
        with _db.connection_context():
            cnt = ProxyIP.update(http_pass_proxy_ip=self.http_pass_proxy_ip, https_pass_proxy_ip=self.https_pass_proxy_ip,
                                 http_anonymous=self.http_anonymous, https_anonymous=self.https_anonymous,
                                 http_weight=self.http_weight, https_weight=self.https_weight,
                                 latency=self.latency, failed_validate=self.failed_validate,
                                 updated_at=datetime.datetime.now()) \
                .where(ProxyIP.ip == self.ip).execute()
            if 0 == cnt:
                cnt = self.save()
        return cnt


ProxyIP.create_table()
ProxyWebSite.create_table()
logger.info("tables created!")