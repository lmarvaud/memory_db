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
from typing import Iterable

from cached_property import cached_property
from django.core.exceptions import FieldDoesNotExist
from django.db.models.fields import Field


class MemoryMeta:
    """Subclass of the MemoryModel Meta classes."""

    pk: Field
    fields: Iterable[Field] = ()

    def __init__(self, cls, name):
        self.object_name = cls.__name__
        self.model_name = name

    @cached_property
    def fields_map(self):
        """Return a map of fields by attname."""
        res = {'pk': self.pk}
        for field in self.fields:
            res[field.name] = field
            # Due to the way Django's internals work, get_field() should also
            # be able to fetch a field by attname. In the case of a concrete
            # field with relation, includes the *_id name too
            try:
                res[field.attname] = field
            except AttributeError:
                pass
        return res

    def get_field(self, field_name):
        """Return a field instance given the name of a forward or reverse field."""
        try:
            # Retrieve field instance by name from cached or just-computed
            # field map.
            return self.fields_map[field_name]
        except KeyError:
            raise FieldDoesNotExist("%s has no field named '%s'" % (self.object_name, field_name))
