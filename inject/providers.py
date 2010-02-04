from inject import scopes
from inject.invoker import Invoker


class Instance(object):
    
    __slots__ = ('inst',)
    
    def __init__(self, inst):
        self.inst = inst
    
    def __call__(self):
        return self.inst


class Factory(object):
    
    instance_class = Instance
    invoker_class = Invoker
    
    def __new__(cls, bindto, scope=None):
        if scope is None and hasattr(bindto, '_inject_scope'):
            scope = bindto._inject_scope
        
        if callable(bindto):
            if hasattr(bindto, 'im_self') and bindto.im_self is None:
                provider = cls.invoker_class(bindto)
            else:
                provider = bindto
        else:
            provider = cls.instance_class(bindto)
        
        if scope is not None and scope is not scopes.no:
            provider = scope.scope(provider)
        
        return provider