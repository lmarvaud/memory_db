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
from typing import Dict, Iterable

from django.db.models.fields import Field

from memory_db.models import MemoryModel

class MemoryMeta:
    pk: Field = ...
    fields: Iterable[Field] = ...
    object_name: str = ...
    model_name: str = ...

    def __init__(self, cls: MemoryModel, name: str):
        ...

    def fields_map(self) -> Dict[str, Field]:
        ...

    def get_field(self, field_name: str) -> Field:
        ...
