import inject
from datetime import datetime
from django.http import HttpResponse



class Hello(object):
    
    '''Hello string with a request counter.'''
    
    counter = 0
    
    def __init__(self):
        self.__class__.counter += 1
    
    def __str__(self):
        s = ''
        if self.counter == 1:
            s = 'Hello! This is the first request.'
        else:
            s = 'Hello! I have served %s requests.' % self.counter
        s += '<br />Don\' forget about favicon requests.'
        return s


class Text1(object):
    
    @inject.param('app_started_at', 'app_started_at')
    def __init__(self, app_started_at):
        self.app_started_at = app_started_at
    
    def __str__(self):
        return 'The application started serving requests at <b>%s</b>.<br />' \
               'This value is application scoped. In other words,<br />' \
               'it has been created only once for the whole<br />' \
               'application.' % self.app_started_at


class Text2(object):
    
    @inject.param('req_started_at', 'req_started_at')
    def __init__(self, req_started_at):
        self.req_started_at = req_started_at
    
    def __str__(self):
        return 'The request started at <b>%s</b>.<br /><br />' \
               'This value is request scoped. In other words,<br />' \
               'it is created only once for each request.' % \
               self.req_started_at


class Text3(object):
    
    @inject.param('req_started_at', 'req_started_at')
    @inject.param('req_ended_at', datetime, bindto=datetime.now)
    def __str__(self, req_started_at, req_ended_at):
        return 'The request ended at <b>%s</b>,<br />' \
               'but started at <b>%s</b>.<br />' \
               'It took <b>%s</b> to serve the request.<br /><br />' \
               'There are two datetime object here, but the first<br />' \
               'is not request scoped (req_ended_at), while the second<br/>' \
               '(req_started_at) is.' % (req_ended_at, req_started_at, 
                                     req_ended_at - req_started_at)


@inject.param('hello', Hello)
@inject.param('text1', Text1)
@inject.param('text2', Text2)
@inject.param('text3', Text3)
def index(request, hello, text1, text2, text3):
    content = []
    content.append(str(hello))
    content.append(str(text1))
    content.append(str(text2))
    content.append(str(text3))
    return HttpResponse('<br /><br />'.join(content))