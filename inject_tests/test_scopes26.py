from inject import scopes

    
def testClassDecorator(self):
    '''Scope decorator should set class's STORE_ATTR if Python2.6+.'''    
    scope = self.scope
    
    @scope
    class A(object): pass
    
    self.assertTrue(getattr(A, scopes.SCOPE_ATTR) is scope)