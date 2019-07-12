import logging, logging.handlers
import sys

_formatter = logging.Formatter(fmt='[%(asctime)s] - %(name)s - %(threadName)s - [%(filename)s:%(lineno)s]- %(levelname)s : %(message)s',
                               datefmt="%Y-%m-%d - %H:%M:%S")
_ch = logging.StreamHandler(sys.stdout)
_ch.setLevel(logging.DEBUG)
_ch.setFormatter(_formatter)

_fh = logging.handlers.RotatingFileHandler("pikapi.log", "a", maxBytes=1000000, backupCount=5)
_fh.setLevel(logging.DEBUG)
_fh.setFormatter(_formatter)

logger = logging.getLogger('pikapi')
logger.setLevel(logging.DEBUG)

logger.addHandler(_ch)
logger.addHandler(_fh)
