'''Example bindings configuration.'''
import inject
from datetime import datetime


# Create and REGISTER it!
injector = inject.Injector()
inject.register(injector)

# Add all your bindings.

# This dependency is instantiated only once for the whole application.
injector.bind('app_started_at', to=datetime.now, scope=inject.appscope)

# Once for every request.
injector.bind('req_started_at', to=datetime.now, scope=inject.reqscope)

# Every time when accessed.
injector.bind('req_ended_at', to=datetime.now)
