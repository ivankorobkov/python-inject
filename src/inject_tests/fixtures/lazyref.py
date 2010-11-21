import inject


class A(object):
    
    b = inject.attr('.B')


class B(object):
    
    pass


class P(object):
    
    q = inject.named_attr('q', '.Q')


class Q(object):
    
    p = inject.named_attr('p', P)


@inject.param('z', '.Z')
def func(z):
    return z


class Z(object):
    
    pass
