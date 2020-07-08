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
import inspect
from typing import Dict, Type

from django.core.checks.messages import Error
from django.core.exceptions import ImproperlyConfigured, ObjectDoesNotExist, ValidationError
from django.db.models.fields import CharField, Field

from .options import MemoryMeta


class MemoryModelBase(type):
    """
    MemoryModel metaclass.

    Will set the objects model and instanciate the Meta class in the _meta var
    """

    def __new__(mcs, name, bases, attrs: dict):
        """Define new class."""
        attrs.setdefault('DoesNotExist', type(name + 'DoesNotExist', (ObjectDoesNotExist, ), {}))
        meta_class = attrs.pop('Meta', None)
        if not meta_class:
            raise ImproperlyConfigured(f'Add Meta class to {name}')
        new_class: Type[MemoryModelBase] = \
            super(MemoryModelBase, mcs).__new__(mcs, name, bases, attrs)
        for attr in attrs.values():
            if not inspect.isclass(attr) and hasattr(attr, 'model'):
                attr.model = new_class
        if not issubclass(meta_class, MemoryMeta):
            raise ImproperlyConfigured(f"{name}'s Meta class is not a MemoryMeta")
        setattr(new_class, '_meta', meta_class(new_class, name))
        return new_class


class MemoryModel(metaclass=MemoryModelBase):
    """MemoryModel is a dictionary.

    To allow using the model the same way the django models works, the attributes
    are also available.

        obj = MemoryModel(xxx=123)
        obj['xxx'] == obj.xxx

    mixing with a MemoryManager to load the data and treat it as a standard QuerySet
    """

    _meta: MemoryMeta

    def __init__(self, **kwargs):
        if 'pk' in kwargs:
            kwargs[self._meta.pk.get_attname()] = kwargs.pop('pk')
        for field in self._meta.fields:
            attname = field.get_attname()
            if attname in kwargs:
                setattr(self, attname, kwargs[attname])
            else:
                setattr(self, attname, None)
        super().__init__()

    def __hash__(self):
        """Model hash."""
        return hash(tuple(self.__dict__.items()))

    def __getattr__(self, key):
        """Item getter."""
        if key == 'pk' and key != self._meta.pk.name:
            key = self._meta.pk.name
            return getattr(self, key)
        return getattr(super(), key)

    @classmethod
    def from_db(cls, row: dict):
        """
        Load a model from rows data.

        Basically map row[field.db_name] to init_kwargs[field.name]
        """
        kwargs = {}
        errors: Dict[str, ValidationError] = {}
        for field in cls._meta.fields:
            attname = field.get_attname()
            column = field.db_column or attname
            if column is not None:
                value = row.get(column, field.get_default())
                if field.blank and value == '':
                    value = field.get_default()
                else:
                    try:
                        value = field.to_python(value)
                    except ValidationError as exc:
                        errors[field.name] = exc
                kwargs[attname] = value
        if errors:
            raise ValidationError(errors)
        return cls(**kwargs)

    @classmethod
    def check_data(cls, row: Dict[str, str]):
        """Check the data of a row according to the model Meta.fields."""
        errors = []
        for field in cls._meta.fields:
            column = field.db_column or field.get_attname()
            if column not in row:
                errors.append(
                    Error(
                        msg='Missing field',
                        id='memory_db.models.E001',
                        obj=f'column {column}',
                    )
                )
            else:
                if field.blank and row[column] == '':
                    value = field.get_default()
                else:
                    value = row[column]
                try:
                    field.clean(value, None)
                except ValidationError as exc:
                    errors.append(
                        Error(
                            msg='Invalid value',
                            hint=', '.join(map(str, exc)),
                            id='memory_db.models.E002',
                            obj=f'column {column}',
                        )
                    )
        return errors

    class Meta(MemoryMeta):
        """Meta data."""

        pk: Field = CharField(name='key')
