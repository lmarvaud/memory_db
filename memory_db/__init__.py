# memory_db
# Copyright (C) 2020  Leni Marvaud
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
"""
Django like model in memory.

See: https://github.com/lmarvaud/memory_db/blob/master/README.md
"""

from .manager import MemoryBaseManager, MemoryManager, MemoryRelatedManager
from .models import MemoryModel
from .options import MemoryMeta
from .query import MemoryQuerySet

__all__ = [
    'MemoryBaseManager',
    'MemoryManager',
    'MemoryMeta',
    'MemoryModel',
    'MemoryQuerySet',
    'MemoryRelatedManager',
]
