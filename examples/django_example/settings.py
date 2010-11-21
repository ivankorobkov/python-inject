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