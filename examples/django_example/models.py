

class Article(object):
    
    def __init__(self, title, text):
        self.title = title
        self.text = text
    
    def __unicode__(self):
        s = u'<h1>%s</h1>' % self.title
        s += u'<p>%s</p>' % self.text
        return s
