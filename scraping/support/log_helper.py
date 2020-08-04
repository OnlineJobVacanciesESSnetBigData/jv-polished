"""
Helper methods for logging
"""

import scraping.support.general_helper as general_helper
from scraping.support.common import *
import logging as lg
import sys


deflog = None

DEFAULT_LOGGER = 'jvp'
LOG_DIR = from_root('log/', create_if_needed=True)[:-1]

FILE_NAME = '{}/{}_{}.log'.format(
    LOG_DIR,
    general_helper.get_date(),
    general_helper.get_time())


def set_file_name(log_file_name):
    global FILE_NAME
    FILE_NAME = '{}/{}.log'.format(LOG_DIR, log_file_name)

    init_def_log(force=True)


def get_file_name():
    return FILE_NAME.split('/')[-1].split('.')[0]


def get_logger(name=DEFAULT_LOGGER):
    logger = lg.getLogger(name)

    if len(logger.handlers) == 0:
        stream_handler = lg.StreamHandler(sys.stdout)
        file_handler = lg.FileHandler(FILE_NAME)
        formatter = lg.Formatter('%(asctime)s  %(levelname)8s  %(name)35s >>> %(message)s')
        file_handler.setFormatter(formatter)
        stream_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)
        logger.setLevel(lg.DEBUG)
        logger.debug('Logger {} initialized'.format(name))

    return logger


def init_def_log(name=DEFAULT_LOGGER, force=False):
    global deflog

    if deflog is None or force:
        if deflog is not None:
            for h in deflog.handlers:
                h.close()
            deflog.handlers.clear()
        deflog = get_logger(name)


init_def_log()