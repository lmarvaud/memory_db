# memory_db
# Copyright (C) 2020 Leni Marvaud
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
import functools
import operator
from typing import Any, Callable, Optional

from memory_db.utils import cast_value


class MemoryFunctions:
    """
    Function registrery.

    Used to add functions to the queryset (equivalent to the lookups in django)

    The @default function use is : exact
    """

    def __init__(self):
        self.__registery = dict()

    def register(
        self, func: Callable[[Any, Any], bool], *, name: Optional[str] = None, default=False
    ):
        """
        Register a new function in the registery.

        By default, the name of the function is the function name
        """
        if default:
            self.default = func
        name = name or func.__name__
        self.__registery[name] = func
        return func

    def registered(self, name):
        """Return True if the function is a registered function."""
        return name in self.__registery

    def get(self, name):
        """Get the function associated to the name."""
        return self.__registery[name]


MEMORY_FUNCTIONS = MemoryFunctions()  # pylint: disable=invalid-name


def cast_op(op):
    """Create an operator with casting method."""

    @functools.wraps(op)
    def wrapper(value, filter_value):
        """Cast and apply the comparaison operator."""
        filter_value = cast_value(value, filter_value)
        return op(value, filter_value)

    return wrapper


def icast_op(op):
    """Create a non sensitive operator."""

    @functools.wraps(op)
    def wrapper(value: str, filter_value: str):
        """Call the comparaison operator with upper strings."""
        assert isinstance(value, str)
        assert isinstance(filter_value, str)
        return op(value.upper(), filter_value.upper())

    return wrapper


def rev_op(op):
    """Create an operator switching the two args."""

    @functools.wraps(op)
    def wrapper(value, filter_value):
        """Call the comparaison operator with upper strings."""
        return op(filter_value, value)

    return wrapper


MEMORY_FUNCTIONS.register(cast_op(operator.eq), name='exact', default=True)
MEMORY_FUNCTIONS.register(icast_op(operator.eq), name='iexact')
MEMORY_FUNCTIONS.register(rev_op(operator.contains), name='in')
MEMORY_FUNCTIONS.register(operator.contains, name='contains')
MEMORY_FUNCTIONS.register(icast_op(cast_op(operator.contains)), name='icontains')
MEMORY_FUNCTIONS.register(cast_op(operator.le), name='lte')
MEMORY_FUNCTIONS.register(cast_op(operator.lt), name='lt')
MEMORY_FUNCTIONS.register(cast_op(operator.ge), name='gte')
MEMORY_FUNCTIONS.register(cast_op(operator.gt), name='gt')
MEMORY_FUNCTIONS.register(str.startswith, name='startswith')
MEMORY_FUNCTIONS.register(icast_op(str.startswith), name='istartswith')
MEMORY_FUNCTIONS.register(str.endswith, name='endswith')
MEMORY_FUNCTIONS.register(icast_op(str.endswith), name='iendswith')


@MEMORY_FUNCTIONS.register
def isnull(value, filter_value):
    """Check if value is considered as NULL."""
    from .manager import MemoryBaseRelatedManager

    if isinstance(value, MemoryBaseRelatedManager):
        isnull = len(value) == 0
    else:
        isnull = (value is None)
    return isnull == filter_value
