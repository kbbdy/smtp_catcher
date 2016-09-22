import logging
from logging.config import dictConfig
from .settings import conf


def level(name):
    ll = {'CRITICAL': logging.CRITICAL,
          'ERROR': logging.ERROR,
          'WARNING': logging.WARNING,
          'INFO': logging.INFO,
          'DEBUG': logging.DEBUG,
          'NOTSET': logging.NOTSET}
    try:
        return ll[name.strip().upper()]
    except KeyError:
        return logging.INFO


logger = logging.getLogger()
logging.getLogger("peewee").setLevel(level(conf.LOGGING_LEVEL))
handler = logging.StreamHandler()
formatter = logging.Formatter(
        '%(processName)-5s %(asctime)s  %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(level(conf.LOGGING_LEVEL))
