import inject


class A(object):
    
    b = inject.attr('inject_tests.fixtures.cyclic2.B')


class A2(object):
    
    b = inject.attr('cyclic2.B')


class P(object):
    
    q = inject.named_attr('q', 'inject_tests.fixtures.cyclic2.Q')


@inject.param('z', 'inject_tests.fixtures.cyclic2.Z')
def func(z):
    return z
