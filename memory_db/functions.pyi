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
from typing import Any, Callable

MemoryFunctionType = Callable[[Any, Any], bool]


class MemoryFunctions:

    def register(self, func: MemoryFunctionType = ..., *, name: str = ...):
        ...

    def default(self) -> MemoryFunctionType:
        ...

    def registered(self, name: str) -> bool:
        ...

    def get(self, name: str) -> MemoryFunctionType:
        ...


MEMORY_FUNCTIONS: MemoryFunctions
