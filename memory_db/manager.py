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

from django.db.models.manager import BaseManager

from .query import MemoryQuerySet


class MemoryBaseManager(BaseManager, metaclass=abc.ABCMeta):
    """MemoryManager meta class overloading the queryset initialization."""

    def get_queryset(self):
        """Get a new QuerySet object.

        Subclasses can override this method to
        easily customize the behavior of the Manager.
        """
        return self._queryset_class(model=self.model, get_all=self.get_all)

    @abc.abstractmethod
    def get_all(self):
        """Return a list with all the data."""


class MemoryManager(
    MemoryBaseManager.from_queryset(MemoryQuerySet), metaclass=abc.ABCMeta
):  # type: ignore
    """Manager for MemoryQueryset.

    should implement the get_all method which should be cached.
    """

    @abc.abstractmethod
    def get_all(self):
        """
        Return a list with all the data.

        Could/should be cached (see. functools.lru_cache)
        """


class MemoryBaseRelatedManager(MemoryBaseManager):
    """Base memory manager."""

    def __init__(self, model):
        super().__init__()
        self._all = list()
        self.model = model

    def add(self, *objects, bulk=False):
        """Add objects to the manager."""
        self._all += objects

    def get_all(self):
        """Get all fields for the manager."""
        return self._all


class MemoryRelatedManager(MemoryBaseRelatedManager.from_queryset(MemoryQuerySet)):
    """Memory manager."""
