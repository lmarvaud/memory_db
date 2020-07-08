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
import itertools
import operator
from typing import Any, Callable, Dict, Generator, Generic, Iterable, Iterator, List, Optional, \
    Tuple, Type, TYPE_CHECKING, TypeVar

from django.core.exceptions import FieldDoesNotExist, MultipleObjectsReturned

from memory_db.functions import MEMORY_FUNCTIONS

if TYPE_CHECKING:
    from .models import MemoryModel

_Tco = TypeVar('_Tco', bound='MemoryModel', covariant=True)


class MemoryQuery:
    """Query for MemoryQuerySet."""

    def __init__(self):
        self.order_by: List[str] = []
        self.filters: List[Tuple[bool, Dict[str, Any]]] = []


class MemoryQuerySet(Generic[_Tco]):
    """
    Queryset like object managing in-memory data.

    Retrieve the data from the model self.model.objects.get_all() method.
    This method should return a list of object containing the objects to filter.
    Also, it [c|sh]ould be cached (see. functools.lru_cache)
    """

    query_class: Type[MemoryQuery] = MemoryQuery

    def __init__(self, model=None, get_all=None):
        """
        Initialize the model to retrieve the data to.

        The _iterator is the current state the queryset. It might be a list, a
        filtered, an ordered or a islice

        get_all: the method to call to get_all data
        """
        self.model = model
        self.object_name = model.__name__
        self.get_all = get_all
        self.query = self.query_class()
        self._iterator: Optional[Iterator] = None
        self._fields: List[str] = []
        self._iterable_method = self._model_iterable
        self._result_cache = None

    __init__.queryset_only = False

    def __iter__(self):
        """
        Loop over the current iterator.

        Note: Once started the iterator is changed you may want to make a deepcopy
        of the queryset
        """
        self._fetch_all()
        return iter(self._result_cache)

    __iter__.queryset_only = False

    def __len__(self):
        """
        Return the len of the current filtered list.

        Note: This method create a list from the current iterator state.
        """
        self._fetch_all()
        return len(self._result_cache)

    __len__.queryset_only = False

    def count(self):
        """Return the count of element in the filtered list."""
        return len(self)

    def __getitem__(self, key):
        """
        Retrieve an object or a list of object.

        Available options:
        self[start:stop:step]: retrieve a list of object
        self[int]: retrieve the nth element of the iterator
        self[str]: equal to self.filter(pk=str)[0]
        """
        self._fetch_all()
        if isinstance(key, slice):
            start = key.start if key.start >= 0 else max(0, len(self._result_cache) + key.start)
            stop = key.stop if key.start >= 0 else max(0, len(self._result_cache) + key.stop)
            step = key.step
            self._iterator = itertools.islice(self._result_cache, start, stop, step)
            self._result_cache = None
            return self
        if isinstance(key, int):
            try:
                return self._result_cache[key]
            except IndexError:
                raise self.model.DoesNotExist(self.query)
        return self.filter(pk=key)[0]

    __getitem__.queryset_only = False

    def __contains__(self, key):
        """Check if a value is contain in the QuerySet."""
        self._fetch_all()
        return key in self._result_cache

    __contains__.queryset_only = False

    def __reversed__(self):
        """Reverse the result."""
        self._fetch_all()
        self.query.order_by.append((True, None))
        self._iterator = reversed(self._result_cache)
        self._result_cache = None
        return self

    __reversed__.queryset_only = False

    def _model_iterable(self):
        for values in self.iterator():
            yield values

    def _values_iterable(self):
        for values in self.iterator():
            values = dict((field, self._get_value(values, field)[0]) for field in self._fields)
            yield values

    def _values_list_iterable(self):
        for values in self.iterator():
            values = tuple(self._get_value(values, field)[0] for field in self._fields)
            yield values

    def _flat_values_list_iterable(self):
        for values in self.iterator():
            value = self._get_value(values, self._fields[0])[0]
            yield value

    def exists(self) -> bool:
        """Return True if the iterable contains at least one object."""
        try:
            next(iter(self))
            return True
        except StopIteration:
            return False

    def first(self):
        """Return the first match or None."""
        return next(iter(self), None)

    def last(self):
        """Return the first match or None."""
        self._fetch_all()
        return next(iter(reversed(self)), None)

    def values(self, *fields):
        """
        Renvoie un QuerySet qui renvoie des dictionnaires lorsqu’on l’utilise de manière itérable.

        au lieu d’instances de modèles.
        """
        self._fields: Iterable[str] = fields
        self._iterable_method: Callable[[], Generator[Any]] = self._values_iterable
        return self

    def values_list(self, *fields, flat=False):
        """
        Semblable à values().

        sauf qu’au lieu de renvoyer des dictionnaires, ce sont des tuples qui
        sont renvoyés lors de l’itération des résultats. Chaque tuple contient les valeurs des
        champs dans la position respective de leur apparition dans l’appel à values_list() —
        premier champ comme premier élément
        """
        self._fields = fields
        self._iterable_method = self._flat_values_list_iterable \
            if flat else self._values_list_iterable
        return self

    def _fetch_all(self):
        if self._result_cache is None:
            self._result_cache = list(self._iterable_method())

    def iterator(self):
        """
        Retrieve the current iterator.

        rtype: Iterable[Model]:
        """
        if self._iterator is None:
            self.all()
        return self._iterator

    @property
    def ordered(self) -> bool:
        """Return true if the query is ordered."""
        return bool(self.query.order_by)

    def order_by(self, *orders):
        """Order the iterator."""
        for order in reversed(orders):
            reverse = False
            if order[0] == '-':
                reverse = True
                order = order[1:]
            if order == 'pk':
                order = self.model._meta.pk.name
            self._iterator = sorted(
                self.iterator(), key=operator.attrgetter(order), reverse=reverse
            )
            self.query.order_by.append(order)
        return self

    def _get_value(self, obj: 'MemoryModel', filter_key: str):
        """Retrieve the filter value in the object."""
        filter_keys = filter_key.split('__')
        function = MEMORY_FUNCTIONS.default
        for key in filter_keys:
            if key == 'pk':
                key = self.model._meta.pk.name
            if not hasattr(obj, key):
                if not MEMORY_FUNCTIONS.registered(key):
                    raise FieldDoesNotExist("%s has no field named '%s'" % (self.object_name, key))
                function = MEMORY_FUNCTIONS.get(key)
            else:
                obj = getattr(obj, key)
        return obj, function

    def get(self, **filters):
        """Retrieve one element."""
        results = self.filter(**filters)
        if len(results) > 1:
            raise MultipleObjectsReturned
        return results[0]

    def filter(self, **filters):  # noqa: A003
        """Filter elements in the iterator."""

        def _filter(obj):
            for filter_key, filter_value in filters.items():
                if filter_key == 'pk':
                    filter_key = self.model._meta.pk.name
                value, function = self._get_value(obj, filter_key)
                if not function(value, filter_value):
                    return False
            return True

        self._iterator = filter(_filter, self.iterator())
        self.query.filters.append((False, filters))
        return self

    def exclude(self, **filters):
        """Filter elements in the iterator."""

        self.query.filters.append((True, filters))

        def _exclude(obj):
            for filter_key, filter_value in filters.items():
                if filter_key == 'pk':
                    filter_key = self.model._meta.pk.name
                value, function = self._get_value(obj, filter_key)
                if function(value, filter_value):
                    return False
            return True

        self._iterator = filter(_exclude, self.iterator())
        return self

    def all(self):  # noqa: A003
        """Reset the iterator to the initial state."""
        self._iterator = self.get_all()
        self.query = self.query_class()
        return self
