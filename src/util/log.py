# -*- coding=utf-8 -*-
import logging
import logging.config

from conf.config import LOGGING_CONFIG


class LogService():

    logging.config.dictConfig(LOGGING_CONFIG)

    @classmethod
    def getLogger(cls):
        return logging.getLogger('root')

if __name__ == '__main__':
    #logger = LogService.getReactionLogger()
    logger = LogService.getLogger()
    logger.info('a test log')
    print __file__
