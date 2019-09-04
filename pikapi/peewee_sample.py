#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import logging
from concurrent.futures.thread import ThreadPoolExecutor
from time import sleep

from peewee import *
import datetime

from playhouse.db_url import connect


logging.basicConfig(level=logging.DEBUG,
                    format='[%(asctime)s] <%(processName)s>%(threadName)s - [%(filename)s:%(lineno)s]%(levelname)5s : %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# db = MySQLDatabase('db1', host='127.0.0.1', user='admin', passwd='123456')
# db.connect()

# db = SqliteDatabase('my_app.db')

#多线程既有更新又有查询，peewee.OperationalError: database is locked
#使用journal_mode=wal可分开读写，避免此错误
# db = SqliteDatabase('my_app.db', pragmas={'journal_mode': 'wal'})

#使用SqliteQueueDatabase将修改只用一个线程，查询仍然并发执行
# db = SqliteQueueDatabase(
#     'my_app.db',
#     use_gevent=False,  # Use the standard library "threading" module.
#     autostart=True,  # The worker thread now must be started manually.
#     queue_max_size=64,  # Max. # of pending writes that can accumulate.
#     results_timeout=5.0)  # Max. time to wait for query to be executed.

#使用连接池方式
db = connect('sqlite+pool:///my_app.db?max_connections=4&stale_timeout=300&timeout=0&check_same_thread=False')
db.journal_mode = 'wal'
# db = connect('mysql+pool://admin:123456@192.168.154.101:3306/db1?max_connections=6&stale_timeout=300&timeout=0')

tpool = ThreadPoolExecutor(40)

for k in dir(db):
    if not k.startswith('_'):
        o = getattr(db, k)
        if type(o) in [tuple, list, str, int, bool]:
            logger.info("{}={}".format(k, str(o)))


class BaseModel(Model):
    class Meta:
        database = db


class Person(BaseModel):
    # 未定义主键，默认会自动加一个id主键
    user_name = CharField(unique=True)
    age = IntegerField()
    created_at = DateTimeField(default=datetime.datetime.now)


class Pet(BaseModel):
    # 未定义主键，默认会自动加一个id主键
    # 外键引用，会添加一个user_id字段
    owner = ForeignKeyField(Person, related_name='pets')
    name = CharField()
    update_at = DateTimeField(default=datetime.datetime.now)
    animal_type = CharField()


def drop():
    db.drop_tables([Pet, ])
    Person.drop_table()


def newdb():
    Person.create_table()
    db.create_tables([Pet, ])
    # 插入数据库并返回该实例
    u = Person.create(user_name='tom', age=5)
    u.age = 6
    u.save()  # 执行update
    kitty = Pet.create(owner=u, name='Kitty', animal_type='cat')
    # with db.connection_context():
    ps = Person.select().where(Person.user_name == 'tom').execute()
    for i, p in enumerate(ps):
        print(p.user_name)

def callback(future):
    try:
        rst = future.result()
    except Exception as e:
        logger.error("thread error %s", e, exc_info=True)


def test_in_threads(fun, num):
    for i in range(num):
        tpool.submit(fun, i).add_done_callback(callback)


def test_update(n):
    while True:
        # with db.connection_context():
        s = Pet.update(update_at=datetime.datetime.now()).where(Pet.name == 'Peppa')
        r = s.execute()
        logger.info('update :%s' % r)
        sleep(1)


def test_query(n):
    while True:
        # with db.connection_context():
        s = Person.select().count()
        logger.info('select :%s' % str(s))
        # p= Person.select()
        # for x in p.iterator():
        #     logger.info('{},{}'.format(x.user_name, x.age))
        sleep(1)


if __name__ == '__main__':
    drop()
    newdb()
    # # test_query()
    # test_in_threads(test_query, 10)
    # test_in_threads(test_update, 10)
    # while True:
    #     logger.info(" main ")
    #     sleep(1)