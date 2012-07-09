try:
    import inject
except ImportError:
    # Must be running without installing python-inject.
    import os
    import sys
    cwd = os.getcwd()
    parent = os.path.normpath(os.path.join(cwd, os.pardir, os.pardir,
                                           'src'))
    sys.path.append(parent)
    import inject


DEBUG = True
TEMPLATE_DEBUG = DEBUG

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': '', # Or path to database file if using sqlite3.
        'USER': '', # Not used with sqlite3.
        'PASSWORD': '', # Not used with sqlite3.
        'HOST': '', # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '', # Set to empty string for default. Not used with sqlite3.
    }
}


MIDDLEWARE_CLASSES = (
    'inject.middleware.DjangoInjectMiddleware',
    
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)

ROOT_URLCONF = 'django_example.urls'

#==============================================================================
# python-inject configuration
#==============================================================================
import inject


def config_bindings(injector):
    from . import bindings
    bindings.config(injector)

# Settings can be imported multiple times.
# This condition prevents AnotherInjectorRegisteredException.
if not inject.is_registered():
    # Lazy injector is created so that django's settings can be accessed
    # in the bindings.py file.
    inject.create_lazy(config_bindings, autobind=False)


TEST_PS = '<p><small>Powered by python-inject</small</p>'
