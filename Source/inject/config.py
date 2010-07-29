'''Default injector configuration, which binds scopes, and the injector.'''
from inject.scopes import ApplicationScope, appscope, \
    NoScope, noscope, \
    RequestScope, reqscope


def default_config(injector):
    from inject.injectors import Injector
    injector.bind(Injector, to=injector)
    
    appscope_instance = ApplicationScope()
    noscope_instance = NoScope()
    reqscope_instance = RequestScope()
    
    injector.bind_scope(ApplicationScope, to=appscope_instance)
    injector.bind_scope(appscope, to=appscope_instance)
    
    injector.bind_scope(NoScope, to=noscope_instance)
    injector.bind_scope(noscope, to=noscope_instance)
    
    injector.bind_scope(RequestScope, to=reqscope_instance)
    injector.bind_scope(reqscope, to=reqscope_instance)
