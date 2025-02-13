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
import sys
from typing import Any, Callable, Collection, Dict, Generic, Iterable, Iterator, List, Optional, \
    overload, Reversible, Sized, Tuple, Type, TypeVar, Union

from memory_db.models import MemoryModel

if sys.version_info >= (3, 11):
    from typing import Self
else:
    Self = TypeVar("Self", bound='_BaseMemoryQuerySet')

_T = TypeVar("_T", bound=MemoryModel, covariant=True)
_Row = TypeVar("_Row", covariant=True)

GetAllFunction = Callable[[], Iterable[_T]]


class MemoryQuery:
    order_by: List[str] = ...
    filters: List[Tuple[Dict[str, Any], bool]] = ...


class _BaseMemoryQuerySet(Generic[_T], Sized):
    """
    Queryset like object managing in-memory data.

    Retrieve the data from the model self.model.objects.get_all() method.
    This method should return a list of object containing the objects to filter.
    Also, it [c|sh]ould be cached (see. functools.lru_cache)
    """

    model: Optional[Type[MemoryModel]] = ...
    object_name: str = ...
    get_all: Optional[GetAllFunction] = ...
    query: MemoryQuery = ...
    query_class: Type[MemoryQuery] = ...

    def __init__(self, model: Type[MemoryModel] = ..., get_all: GetAllFunction = ...):
        ...

    def __iter__(self) -> Iterator[_T]:
        ...

    def __len__(self) -> int:
        ...

    def __getitem__(self, key: Union[str, int, slice]) -> _T:
        ...

    def exists(self) -> bool:
        ...

    def first(self) -> _T:
        ...

    def values(self, *fields) -> 'ValuesMemoryQuerySet'[_T, Dict[str, Any]]:
        ...

    def values_list(self, *fields, flat: bool = ...) -> 'ValuesMemoryQuerySet'[_T, Any]:
        ...

    def __contains__(self, key: Any) -> bool:
        ...

    def __reversed__(self) -> Iterator[_T]:
        ...

    def iterator(self) -> Iterator[_T]:
        ...

    @property
    def ordered(self) -> bool:
        ...

    def order_by(self: Self, *orders: Tuple[str, ...]) -> Self:
        ...

    def get(self: Self, **filters: Dict[str, Any]) -> _T:
        ...

    def filter(self: Self, **filters: Dict[str, Any]) -> Self:
        ...

    def exclude(self: Self, **filters: Dict[str, Any]) -> Self:
        ...

    def all(self: Self) -> Self:
        ...


class MemoryQuerySet(_BaseMemoryQuerySet[_T], Collection[_T], Reversible[_T], Sized):
    ...


class ValuesMemoryQuerySet(_BaseMemoryQuerySet[_T], Collection[_Row], Sized):

    def __contains__(self, x: object) -> bool:
        ...

    def __iter__(self) -> Iterator[_Row]:  # type: ignore
        ...

    @overload  # type: ignore
    def __getitem__(self: Self, i: int) -> _Row:
        ...

    @overload  # type: ignore
    def __getitem__(self: Self, s: slice) -> Self:
        ...

    def iterator(self, chunk_size: int = ...) -> Iterator[_Row]:  # type: ignore
        ...

    def get(self, **filters: Any) -> _Row:  # type: ignore
        ...

    def earliest(self, *fields: Any, field_name: Optional[Any] = ...) -> _Row:  # type: ignore
        ...

    def latest(self, *fields: Any, field_name: Optional[Any] = ...) -> _Row:  # type: ignore
        ...

    def first(self) -> Optional[_Row]:  # type: ignore
        ...

    def last(self) -> Optional[_Row]:  # type: ignore
        ...
