'''Stdout handler configuration for the C{"inject"} logger.'''
import sys
import logging
import threading


_lock = threading.Lock()
_has_stdout_handler = False


def configure_stdout_handler():
    '''Create an stdout logging handler for the C{"inject"} logger.'''
    global _has_stdout_handler
    
    with _lock:
        if _has_stdout_handler:
            return
        _has_stdout_handler = True
        
        logger = logging.getLogger('inject')
        logger.setLevel(logging.DEBUG)
        
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s %(name)s: %(message)s'))
        
        logger.addHandler(handler)
