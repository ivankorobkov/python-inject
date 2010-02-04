from inject.scopes import \
    no as no_scope, \
    app as app_scope, \
    request as request_scope
from inject.invoker import Invoker
from inject.injector import Injector, register, unregister
from inject.injections import attr, param, super_param as super