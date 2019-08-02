import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s-[line:%(lineno)d]%(levelname)5s: %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.FATAL)

if __name__ == '__main__':
    logger.debug("调试级:%s", '参数1')
    logger.info("信息")
    logger.warning("警告")
    try:
        1/0
    except Exception as e:
        logger.error("错误%s", e, exc_info=True)
    logger.critical("严重")
    logger.fatal("致命")
