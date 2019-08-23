#!/usr/bin/python
import logging
import sqlite3
import threading
from time import sleep

logger = logging.getLogger('sqlite')
logger.setLevel(logging.DEBUG)


def singleton(cls):
    _lock = threading.Lock()
    dc = {}

    def instance(*args):
        with _lock:
            if cls not in dc:
                dc[cls] = cls(*args)
            return dc[cls]
    return instance


# @singleton
class SqliteClient:

    def __init__(self, db_name):
        # db_file = ":memory:"
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        # conn.execute('pragma journal_mode=wal')
        logger.info('connection established! {}-{}'.format(id(self), id(self.conn)))

    def __str__(self):
        return "id:%s,conn:%s"%(id(self), id(self.conn))

    @staticmethod
    def log(sql, *args):
        # lst = [str(s) for s in args]
        # s = ','.join(lst)
        # logger.debug('%s,%s' % (sql, s))
        logger.debug('%s %s' % (sql, str(*args)))

    @staticmethod
    def dict_factory(cursor, row):
        d = {}
        for i, col in enumerate(cursor.description):
            d[col[0]] = row[i]
        return d

    def close(self):
        if self.conn is not None:
            self.conn.close()

    def query_page(self, sql, page, num, *args):
        count = self.count(sql, *args)
        ps = "select * from ({}) limit {} offset {}".format(sql, num, page)
        self.log(ps, *args)
        cursor = self.conn.cursor()
        rst = cursor.execute(ps, *args).fetchall()
        cursor.close()
        return count, rst

    def query(self, sql, *args):
        self.log(sql, *args)
        cursor = self.conn.cursor()
        res = cursor.execute(sql, *args).fetchall()
        cursor.close()
        return res

    def execute(self, sql, *args):
        self.log(sql, *args)
        cursor = self.conn.cursor()
        res = cursor.execute(sql, *args).fetchall()
        self.conn.commit()
        cursor.close()
        return res

    def column_names(self, sql, *args):
        self.log(sql, *args)
        cursor = self.conn.cursor()
        cursor.execute(sql + ' limit 0', *args)
        res = [tuple[0] for tuple in cursor.description]
        cursor.close()
        return res

    def get_one(self, sql, *args):
        self.log(sql, *args)
        cursor = self.conn.cursor()
        rows = cursor.execute(sql, *args).fetchone()
        cursor.close()
        res = None
        if rows and len(rows) >= 1:
            res = rows[0]
        return res

    def count(self, sql, *args):
        sql = "select count(*) cnt from ( " + sql + " ) "
        self.log(sql, *args)
        cursor = self.conn.cursor()
        rst = cursor.execute(sql, *args).fetchone()
        cursor.close()
        return rst['cnt']


def main():
    db = SqliteClient('db1.db')
    db.execute(
        '''
        create table if not exists student(
          id   INTEGER primary key autoincrement,
          name  VARCHAR(16) not null,
          create_time  datetime default (datetime('now', 'localtime')),
          addr  text
        )
        '''
    )
    psql = "insert into student (name,addr)values(?,?)"
    for i in range(3):
        db.execute(psql, ('zs-%i' % i, 'fuzhou'))

    # print(db.column_names("select * from student where name = ? ", ('zs-2',)))
    # print(db.count("select * from student where name=? ", ('zs-2',)))
    print(db.get_one("select * from student where id = ? ", (2,)))
    # print(db.query("select * from student where id=? and name=? ", (20, 'zs-2')))
    # print(db.query_page("select * from student where name like ? ", 1, 1000, ("zs%",)))
    # db.execute("update student set name='nameupdate' where id = ? ", ("20",))
    db.close()


if __name__ == '__main__':
    main()
