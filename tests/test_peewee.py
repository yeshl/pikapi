import logging
import random
import socket
import struct
import unittest
from time import sleep

from pikapi.database import create_connection, ProxyIP

# logger = logging.getLogger('pikapi.test')
logger = logging.getLogger('peewee')
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())


def gen_random_ip() -> str:
    return socket.inet_ntoa(struct.pack('>I', random.randint(1, 0xffffffff)))


class Test(unittest.TestCase):
    def test(self):
        db = create_connection()

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

    def testFeedFromDb(self):
        # proxies = ProxyIP.select().where((ProxyIP.updated_at < datetime.now() - timedelta(minutes=5))
        #                                  & (ProxyIP.https_weight > 0) & (ProxyIP.http_weight > 0))
        while True:
            proxies = ProxyIP.select(ProxyIP.ip).where((ProxyIP.https_weight > 0) & (ProxyIP.http_weight > 0)) \
                .where(ProxyIP.updated_at > "datetime('now','-1 hour','localtime')")
            for x in proxies.iterator():
                print(x.ip)
            sleep(1)
        # count = proxies.count()
        # assert count > 0
        # logger.info(count)


if __name__ == '__main__':
    suite = unittest.TestSuite()
    test_cases = [Test("testFeedFromDb")]
    suite.addTests(test_cases)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
