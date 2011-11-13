import inject
from models import Article
from django.http import HttpResponse


@inject.param('article', Article)
def index(request, article):
    return HttpResponse(unicode(article))
