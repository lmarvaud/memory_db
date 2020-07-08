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
from typing import Iterable, TYPE_CHECKING

from django.db.models import CharField, Field, IntegerField

from memory_db import MemoryBaseManager, MemoryMeta, MemoryModel, MemoryQuerySet


class TestMemoryQuerySet(MemoryQuerySet):
    """Test queryset."""

    def __eq__(self, value: object) -> bool:
        """Compare queryset result with a list."""
        return list(self) == value

    def __repr__(self):
        """
        Test memory Queryset representation.

        To get pretty errors during tests.
        """
        return f'{list(self)!r}'


if TYPE_CHECKING:
    TestMemoryBaseManager = MemoryBaseManager['TestMemoryModel']
else:
    TestMemoryBaseManager = MemoryBaseManager.from_queryset(TestMemoryQuerySet)


class TestMemoryManager(TestMemoryBaseManager):
    """Test manager."""

    def get_all(self):
        """Memory for tests data."""
        one = self.model(pk=1, value='One')
        two = self.model(pk=2, value='Two')
        three = self.model(pk=3, value='Three')
        return [one, two, three]


class TestEmptyManager(TestMemoryBaseManager):  # type: ignore
    """Test manager without elements."""

    @staticmethod
    def get_all():
        """Nothing return for this "empty" manager."""
        return []


class TestMemoryModel(MemoryModel):
    """Test model."""

    objects = TestMemoryManager()
    none = TestEmptyManager()

    pk: int
    value: str

    def __eq__(self, right):
        """Compare models."""
        return self.pk == right.pk and self.value == right.value

    def __repr__(self):
        """Memory model representation."""
        return f'MemoryModel(pk={self.pk!r}, value={self.value!r})'

    class Meta(MemoryMeta):
        """Test model parameters."""

        pk: Field = IntegerField(primary_key=True, name='id')
        fields: Iterable[Field] = [
            pk,
            CharField(name='value'),
        ]
