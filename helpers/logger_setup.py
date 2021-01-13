from logging import addLevelName
from logging.config import dictConfig
from logging import getLogger
from datetime import datetime
from os.path import dirname
from os.path import join
from os.path import isdir
from os import makedirs


LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'file': {
            'format': '%(asctime)s | %(name)s:%(levelname)s | '
                      '%(module)s:%(funcName)s:%(lineno)d | %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
        'console': {
            'format': '%(asctime)s | %(levelname)s | %(module)s:%(lineno)d | %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        }
    },
    'handlers': {
        'console': {
            'level': 'CRITICAL',
            'formatter': 'console',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',  # Default is stderr
        },
        'file': {
            'level': 'ERROR',
            'formatter': 'file',
            'class': 'logging.FileHandler',
            'encoding': 'utf-8',
            'filename': 'app.log'
        }
    },
    'loggers': {
        'root': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': False
        },
        'child': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': False
        }
    }
}
LOG_LEVEL_MAP = {
    10: 'DEBUG',
    20: 'INFO',
    30: 'WARNING',
    40: 'ERROR',
    50: 'CRITICAL'
}
LOG_COLOR_MAP = {
    'DEBUG': '\x1b[32;1m',  # green
    'INFO': '\x1b[34;1m',  # blue
    'WARNING': '\x1b[33;1m',  # yellow
    'ERROR': '\x1b[31;1m',  # red
    'CRITICAL': '\x1b[31;7m'  # bg: red | fg: black
}
LOG_LOCATION = join(dirname(dirname(__file__)), 'logs')


def get_log_file():
    """
        # TODO: to be added...
        - generates a file based on execution time and return the path
    """
    date_format, time_format = '%Y-%m-%d', '%H_%M_%S'
    current_date_time = datetime.today()
    date = datetime.strftime(current_date_time, date_format)
    time = datetime.strftime(current_date_time, time_format)
    log_location = join(LOG_LOCATION, date)
    if not(isdir(log_location)):
        makedirs(log_location)
    log_file_name = join(log_location, f'{time}.log')
    return log_file_name


def update_logging_config(name, level, console):
    """
        # TODO: to be added..
        - adds level, file
    """
    # update logging config based on user input
    for handler in LOGGING_CONFIG['handlers']:
        LOGGING_CONFIG['handlers'][handler]['level'] = level

    # create logger for console
    if console:
        LOGGING_CONFIG['loggers'][name]['handlers'].append('console')

    # create a log file...
    LOGGING_CONFIG['handlers']['file']['filename'] = get_log_file()


def get_logger(name, level='ERROR', console=False, colored=False):
    """
        Initialize & return logger
        :param name: name of the logger
        :param level: logging level, default='WARNING'
        :param console: creates a logger console display, default=False
        :param colored: color highlight log level based on severity(recommended for logging to console), default=False
        :return: logger object
    """
    name = 'root' if name == '__main__' else 'child'
    if name == 'root':
        update_logging_config(name, level, console)
    # load logging config
    dictConfig(LOGGING_CONFIG)
    # init logger
    logger = getLogger(name)
    # add color support for log level
    if colored:
        for level, label in LOG_LEVEL_MAP.items():
            color = LOG_COLOR_MAP.get(label, '\x1b[0m')
            addLevelName(level, f'{color}{label}\x1b[0m')
    return logger


if __name__ == '__main__':
    logger = get_logger(__name__, level='DEBUG', console=True, colored=True)
    logger.debug('test debug')
    logger.info('test info')
    logger.warning('test warning')
    logger.error('test error')
    logger.critical('test critical')
