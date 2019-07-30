import logging
import random
import socket
import struct
import unittest

from pikapi.database import create_connection, create_db_tables, ProxyIP

# Add logging
logger = logging.getLogger('peewee')
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())

# logger = logging.getLogger('pikapi.test')


def gen_random_ip() -> str:
    return socket.inet_ntoa(struct.pack('>I', random.randint(1, 0xffffffff)))


class TestProvider(unittest.TestCase):
    def test(self):
        db = create_connection()
        create_db_tables()

    @staticmethod
    def delete_ip(ip: str):
        ProxyIP.delete().where(ProxyIP.ip == ip).execute()

    def test_create_ip(self):
        ip_str = gen_random_ip()
        ip = ProxyIP(ip=ip_str, port=3306)
        ip.save()

        count = ProxyIP.select().count()
        assert count > 0

        self.delete_ip(ip_str)


if __name__ == '__main__':
    unittest.main()
