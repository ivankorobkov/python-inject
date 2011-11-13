'''Example bindings configuration.'''
import inject
from django.conf import settings # To test circular imports.
# Always include django project name in the import name, because
# django_example.models and models can be different modules (WTF?)
# with different classes.
from django_example.models import Article


def config(injector):
    '''Configure injector bindings.'''
    article = Article('Motto', 'Don\'t worry, just make an effort.' + 
                      settings.TEST_PS)
    injector.bind(Article, article)
