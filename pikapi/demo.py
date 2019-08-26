import json
import logging

from pikapi.store import ProxyWebSite, G_PROXY_WEB

logging.basicConfig(level=logging.DEBUG,
                    format='[%(asctime)s] <%(processName)s>%(threadName)s - [%(filename)s:%(lineno)s]%(levelname)5s : %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


def test():
    s=[]
    print(s)
    s.sort(key=lambda x: x, reverse=True)
    print(ss)

if __name__ == '__main__':
   test()
