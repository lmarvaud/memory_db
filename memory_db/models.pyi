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
from typing import Any, Dict, Iterable, Type, TypeVar

from django.core.checks.messages import CheckMessage
from django.core.exceptions import ObjectDoesNotExist

from memory_db.manager import MemoryBaseManager
from memory_db.options import MemoryMeta

_T = TypeVar("_T", bound='MemoryModel', covariant=True)


class MemoryModelBase(type):
    ...


class MemoryModel(metaclass=MemoryModelBase):
    _meta: MemoryMeta = ...
    objects: MemoryBaseManager['MemoryModel']
    DoesNotExist: ObjectDoesNotExist = ...

    class Meta(MemoryMeta):
        ...

    def __init__(self, **kwargs: Any):
        ...

    @classmethod
    def from_db(cls: Type[_T], row: Dict[str, Any]) -> _T:
        ...

    @classmethod
    def check_data(cls, row: Dict[str, str]) -> Iterable[CheckMessage]:
        ...
