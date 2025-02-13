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
import abc
from typing import Iterable, List, Mapping, Optional, Type, TypeVar, Union

from memory_db.models import MemoryModel
from memory_db.query import MemoryQuerySet

_Tco = TypeVar("_Tco", bound=MemoryModel, covariant=True)
_T = TypeVar("_T", bound=MemoryModel)


class MemoryBaseManager(MemoryQuerySet[_Tco], metaclass=abc.ABCMeta):
    """MemoryManager meta class overloading the queryset initialization."""

    name: str = ...
    model: Type[_Tco] = ...

    def get_queryset(self) -> MemoryQuerySet[_Tco]:
        ...

    @abc.abstractmethod
    def get_all(self) -> Iterable[_Tco]:
        ...

    @classmethod
    def from_queryset(
        cls,
        queryset_class: Type[MemoryQuerySet[_Tco]],
        class_name: Optional[str] = ...
    ) -> Type[Union[MemoryQuerySet[_Tco], 'MemoryBaseManager']]:
        ...


class MemoryManager(MemoryBaseManager[_Tco], metaclass=abc.ABCMeta):
    ...


class MemoryBaseRelatedManager(MemoryBaseManager[_Tco]):

    def __init__(self, model: Type[_Tco]):
        ...

    def add(self, *objects: _T, bulk=False):
        ...

    def append(self, object: _T):
        ...

    def get_all(self) -> Iterable[_Tco]:
        ...


class MemoryRelatedManager(MemoryBaseRelatedManager[_Tco]):

    def __init__(self, model: Type[_Tco]):
        ...
