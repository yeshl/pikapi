import logging
import multiprocessing
import threading

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s-[line:%(lineno)d]%(levelname)5s: %(message)s',
                    datefmt='[%Y-%m-%d %H:%M:%S]')
logger = logging.getLogger()

if __name__ == '__main__':
    pn = multiprocessing.current_process().name
    if 'MainProcess' != pn and len(pn.split('-')) > 1:
        logger.debug('thread: %s', pn.split('-')[1])
