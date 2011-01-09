'''Default injector configuration, which binds scopes, and the injector.'''
from inject.log import logger
from inject.scopes import ApplicationScope, appscope, \
    NoScope, noscope, \
    RequestScope, reqscope, ThreadScope, threadscope


def default_configuration(injector):
    from inject.injectors import Injector
    injector.bind(Injector, to=injector)
    
    appscope_instance = ApplicationScope()
    injector.bind(ApplicationScope, to=appscope_instance)
    injector.bind(appscope, to=appscope_instance)
    
    noscope_instance = NoScope()
    injector.bind(NoScope, to=noscope_instance)
    injector.bind(noscope, to=noscope_instance)
    
    thread_scope_instance = ThreadScope()
    injector.bind(ThreadScope, to=thread_scope_instance)
    injector.bind(threadscope, to=thread_scope_instance)
    
    reqscope_instance = RequestScope()
    injector.bind(RequestScope, to=reqscope_instance)
    injector.bind(reqscope, to=reqscope_instance)
    
    logger.debug('Configured injector %r using the default config.',
                 injector)
