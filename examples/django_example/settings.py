try:
    import inject #@UnusedImport
except ImportError:
    # Must be running without installing the inject package.
    import os
    import sys
    cwd = os.getcwd()
    parent = os.path.normpath(os.path.join(cwd, os.pardir, os.pardir,
                                           'Source'))
    sys.path.append(parent)

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
# Don't forget to import the bindings
#==============================================================================
import bindings #@UnusedImport
