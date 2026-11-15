"""Static-typing regression guard for ``inject.Injector.get_instance``."""

import typing as t

import inject


class _Service:
    pass


injector = inject.Injector()

t.assert_type(injector.get_instance(_Service), _Service)
t.assert_type(injector.get_instance("service"), inject.Injectable)
