"""Static-typing regression guard for ``inject.attr``."""

from typing_extensions import assert_type

import inject


class _Service:
    pass


class _Repository:
    pass


assert_type(inject.attr(_Service), _Service)
assert_type(inject.attr(_Repository), _Repository)
