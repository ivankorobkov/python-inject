'''Default logging configuration, used when the injector echo flag is set to
True.
'''
import sys
import logging


class NullHandler(logging.Handler):
    
    '''NullHandler does nothing but prevents messages "No handlers could be 
    found..."
    '''
    
    def emit(self, record):
        pass


def configure_null_handler(logger_name):
    handler = NullHandler()
    logger = logging.getLogger(logger_name)
    logger.addHandler(handler)

configure_null_handler('inject')


def configure_stdout_handler(logger_name):
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s %(name)s: %(message)s'))
    
    logger.addHandler(handler)
