'''Example bindings configuration.'''
import inject
from datetime import datetime


# Create an injector and add bindings.
injector = inject.Injector()
injector.bind('app_started_at', to=datetime.now, scope=inject.appscope)
injector.bind('req_started_at', to=datetime.now, scope=inject.reqscope)

# REGISTER THE INJECTOR!
# So that it is used to get instances.
inject.register(injector)