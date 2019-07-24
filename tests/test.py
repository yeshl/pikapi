import logging

from pyquery import PyQuery

logger = logging.getLogger(__name__)


def craw():
    pq = PyQuery(url="https://www.kuaidaili.com/free/")
    info = pq("#list > table > tbody > tr")
    for tr in info.items():
        ip = tr("td:first-child").text()
        port = tr("td").eq(1).text()
        print(ip, port)


if __name__ == '__main__':
    logger.info('test.......')
