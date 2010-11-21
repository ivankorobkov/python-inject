'''Tutorial code, requires Python2.6 (because of class decorators).'''
try:
    import inject
except ImportError:
    # Must be running without installing the inject package.
    import os
    import sys
    cwd = os.getcwd()
    parent = os.path.normpath(os.path.join(cwd, os.pardir, 'Source'))
    sys.path.append(parent)

import inject
from cgi import parse_qs
from datetime import datetime
from wsgiref.simple_server import make_server
from inject.middleware import WsgiInjectMiddleware


@inject.appscope        # By default, use application scope when the class
class Database(object): # is injected. In other words, instantiate it only
                        # once for the whole application.

    '''Fake database stores all messages in a list.'''
    
    def __init__(self, host, port, user, password):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.messages = []
    
    def insert(self, message):
        self.messages.append(message)
    
    def select(self, order_by_date=False):
        messages = list(self.messages)
        if order_by_date:
            messages.reverse()
        return messages


@inject.appscope        # We don't need multiple repository instances either.
class Repository(object):
    
    '''Repository connects a model and a database, in Django it is
    called a manager.
    '''
    
    # Inject a database instance into the method.
    @inject.param('database', Database)
    def __init__(self, database):
        self.database = database
    
    def all(self):
        return self.database.select(order_by_date=True)
    
    def save(self, message):
        self.database.insert(message)


class Message(object):

    '''Message is our model, it uses the ActiveRecord pattern to communicate
    with the database via a repository, yet implements only the save method. 
    '''

    # Inject a repository instance via a descriptor (similar to a property).
    repository = inject.attr('repository', Repository)
    
    @inject.param('created_at', datetime.now)
    def __init__(self, title, text, created_at):
        self.title = title
        self.text = text
        self.created_at = created_at
    
    def save(self):
        self.repository.save(self)


@inject.reqscope            # When injecting, instantiate only once
class Controller(object):   # for each request.

    '''Controller is used by the application to generate the page,
    and add messages.
    '''
    
    message_class = Message
    repository = inject.attr('repository', Repository)
    
    def show_page(self):
        r = []
        r.append(self.welcome())
        r.append(self.form())
        r.append(self.messages())
        return '<br />'.join(r)
    
    def add_message(self, environ):
        clength = environ.get('CONTENT_LENGTH', 0)
        try:
            clength = int(clength)
        except ValueError:
            clength = 0
        post_string = environ['wsgi.input'].read(clength)
        post = parse_qs(post_string)
        
        title = post['title'][0]
        text = post['text'][0]
        
        message = self.message_class(title=title, text=text)
        message.save()
    
    def welcome(self):
        return 'Welcome to the app built with dependency injection.'
    
    def form(self):
        return '<form method="post" action="">' \
               '<b>Write a message:</b><br />' \
               '<label>Title: <input type="text" name="title" /></label>' \
               '<br />' \
               '<textarea name="text" style="width:200px; height:100px;">'\
               '</textarea><br />' \
               '<input type="submit" name="submit" value="Send">' \
               '</form>'
    
    def messages(self):
        messages = self.repository.all()
        r = []
        for message in messages:
            r.append('<strong>%s</strong>' % message.title)
            r.append('<em>%s</em>' % message.created_at)
            r.append('%s<br />' % message.text)
        return '<br/>'.join(r)


class Application(object):
    
    def __call__(self, environ, start_response):
        start_response('200 OK', [('Content-Type', 'text/html')])
        
        if environ['REQUEST_METHOD'] == 'POST':
            self.add_message(environ)
        
        return self.show_page()
    
    @inject.param('controller', Controller)
    def add_message(self, environ, controller):
        controller.add_message(environ)
    
    @inject.param('controller', Controller)
    def show_page(self, controller):
        return controller.show_page()


config = {
    'db': {
        'host': 'localhost',
        'port': None,
        'user': 'root',
        'password': '123'
    } 
}


@inject.param('config')
def connect_to_db(config):
    '''Get database config and return its instance.'''
    dbconfig = config['db']
    host = dbconfig['host']
    port = dbconfig['port']
    user = dbconfig['user']
    password = dbconfig['password']
    
    return Database(host, port, user, password)


injector = inject.Injector()
injector.bind('config', to=config)
injector.bind(Database, to=connect_to_db, scope=inject.appscope)
inject.register(injector) # Register the injector!


app = Application()
scoped_app = WsgiInjectMiddleware(app)
httpd = make_server('', 8000, scoped_app)
print 'Serving HTTP on port 8000...'
httpd.serve_forever()