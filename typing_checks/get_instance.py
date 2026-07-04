"""Static-typing regression guard for ``inject.Injector.get_instance``."""

from typing_extensions import assert_type

import inject


class _Service:
    pass


injector = inject.Injector()

assert_type(injector.get_instance(_Service), _Service)
assert_type(injector.get_instance("service"), inject.Injectable)
