import logging

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s-[line:%(lineno)d]%(levelname)5s: %(message)s',
                    datefmt='[%Y-%m-%d %H:%M:%S]')
logger = logging.getLogger()

if __name__ == '__main__':
    dic = {'a': '1', 'b': '2'}
    logger.info("abc-%s", dic)
