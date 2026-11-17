"""Static-typing regression guard for ``inject.attr``."""

import typing as t

import inject


class _Service:
    pass


class _Repository:
    pass


t.assert_type(inject.attr(_Service), _Service)
t.assert_type(inject.attr(_Repository), _Repository)
