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
from typing import Iterable, List
from unittest import TestCase

from django.db.models import Field

from memory_db import MemoryManager, MemoryMeta, MemoryModel, MemoryRelatedManager


class MemoryManagerTestRelated(MemoryManager):
    """Manager with relations."""

    def get_all(self) -> Iterable['MemoryModelTestRelated']:
        """Create test models with relation."""
        _1st = MemoryModelTestRelated()
        _2nd = MemoryModelTestRelated()
        _3rd = MemoryModelTestRelated()
        _4th = MemoryModelTestRelated()
        _1st.others.add(_2nd, _3rd, _4th)
        return [_1st, _2nd, _3rd, _4th]


class MemoryModelTestRelated(MemoryModel):
    """Test Model."""

    objects = MemoryManagerTestRelated()

    others: 'MemoryRelatedManager[MemoryModelTestRelated]'

    class Meta(MemoryMeta):
        """Test Model options."""

        pk = None
        fields: List[Field] = []

    def __init__(self):
        """Init the MemoryRelatedManager."""
        super().__init__()
        self.others = MemoryRelatedManager(MemoryModelTestRelated)


class TestMemoryRelatedManager(TestCase):
    """Test MemoryRelatedManager."""

    def test_add(self):
        """Test MemoryRelatedManager add."""
        model = MemoryModelTestRelated()
        other = MemoryModelTestRelated()

        model.others.add(other)

        self.assertEqual(len(model.others), 1)
        self.assertEqual(model.others.get(), other)

    def test_filter(self):
        """Test MemoryRelatedManager filter."""
        self.assertEqual(MemoryModelTestRelated.objects.filter(others__isnull=True).count(), 3)
        self.assertEqual(MemoryModelTestRelated.objects.filter(others__isnull=False).count(), 1)


if __name__ == '__main__':
    from unittest import main

    main()
