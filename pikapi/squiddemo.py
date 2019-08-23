import logging
import random
import time
from datetime import datetime, timedelta

import requests

from pikapi.database import ProxyIP

requests.packages.urllib3.disable_warnings()

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s-[line:%(lineno)d]%(levelname)5s: %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# logger = logging.getLogger('peewee')
# logger.setLevel(logging.DEBUG)
# logger.addHandler(logging.StreamHandler())


def test_squid():
    # r = requests.get('http://192.168.154.101:8899/api?format=csv', timeout=(3, 7))
    # arr = [p.split(':') for p in r.text.split(',')]
    arr = [['192.168.0.242', '3128']]
    # proxies = {'https': 'https://{}:{}'.format('192.168.3.201', 4128)}
    for i in range(10000):
        resp = None
        try:
            ip = random.choice(arr)
            logger.info('req:{} -x {}'.format(i, ip))
            resp = requests.get('https://pv.sohu.com/cityjson',
                             proxies={'https': 'https://{}:{}'.format(ip[0], ip[1])},
                             headers={
                                 'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36',
                                 'Connection': 'keep-alive'},
                             verify=False,
                             timeout=(5, 20))
            logger.info(resp.text)
        except Exception as e:
            logger.info('ERROR %s' % str(e))
        finally:
            if resp is not None:
                resp.close()


def test1():
    for i in range(10):
        proxies = ProxyIP.select().where((ProxyIP.updated_at < datetime.now() - timedelta(minutes=5))
                                         & (ProxyIP.https_weight > 0) & (ProxyIP.http_weight > 0))
        for p in proxies:
            pass
        time.sleep(3)


if __name__ == '__main__':
    test_squid()
