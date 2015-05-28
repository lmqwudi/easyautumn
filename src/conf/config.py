# -*- coding:utf-8 -*-

import os
import sys

CURRENT_DIR = os.path.dirname(__file__) or '.'
PREFIX = ''

####################################
# DB
####################################
DB_HOST_CONFIG = {
    'boring': {
        'host_url': 'mysql://root:mingquan1234@182.92.233.150:3306/boring',
        'kws': {
            'connect_args': {
                'charset': 'utf8',
            },
            'pool_recycle': 1800,
            'echo': False,
        },
    },
}


# logging settings
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simpleFormatter': {
            'format': '%(asctime)s - [%(levelname)s] - %(module)s.%(funcName)s:%(lineno)d - %(message)s',
            'datefmt': '%Y%m%d %H:%M:%S'
        },
    },
    'handlers': {
        'consoleHandler': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simpleFormatter',
            'stream': sys.stdout,
        },
        'standFileHandler': {
            'level': 'DEBUG',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'formatter': 'simpleFormatter',
            'filename': CURRENT_DIR + '/../../logs/stdout.log',
            'when': 'D',
            'interval': 1,
            'backupCount': 60,
        },
    },
    'loggers': {
        'root': {
            'level': 'DEBUG',
            'handlers': ['standFileHandler', 'consoleHandler'],
        },
    },
}


settings = dict(
    template_path=os.path.join(CURRENT_DIR, '../../', 'templates'),
    static_path=os.path.join(CURRENT_DIR, '../../', 'static'),
    debug=True
)
