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
from unittest import TestCase

import django
from django.core.checks.messages import Error
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.db.models.fields import IntegerField, PositiveIntegerField

from memory_db import MemoryMeta, MemoryModel
from tests.models import TestEmptyManager
from tests.utils import setup_django

if django.VERSION < (2, 3):
    expected_error_fmt = "'%s' value must be an integer."
else:
    expected_error_fmt = '“%s” value must be an integer.'


class TestModel(TestCase):
    """Test case on the Model class."""

    class TestModel(MemoryModel):
        """Model to test Model."""

        objects = TestEmptyManager()

        class Meta(MemoryMeta):
            """Test model configuration."""

            pk: IntegerField = PositiveIntegerField(
                name='id', primary_key=True, unique=True, null=False
            )
            fields = [
                pk,
                IntegerField(name='value', null=True, blank=True),
                IntegerField(name='default', blank=True, default=2),
            ]

    def test_empty_model(self):
        """Test MemoryModel invalid meta class."""

        with self.assertRaisesRegex(ImproperlyConfigured, 'Add Meta class to EmptyMetaModel'):

            class EmptyMetaModel(MemoryModel):
                objects = TestEmptyManager()

        with self.assertRaisesRegex(
            ImproperlyConfigured, 'MemoryMetaModel\'s Meta class is not a MemoryMeta'
        ):

            class MemoryMetaModel(MemoryModel):
                objects = TestEmptyManager()

                class Meta:
                    pass

    def test_init(self):
        """Test MemoryModel.__init__ method."""
        result = self.TestModel()

        msg = 'init should create all fields attrs'
        self.assertTrue(hasattr(result, 'pk'), msg)
        self.assertTrue(hasattr(result, 'value'), msg)
        self.assertTrue(hasattr(result, 'default'), msg)
        msg = 'default value shouldn\'t be use on init'
        self.assertIsNone(result.pk, msg)
        self.assertIsNone(result.value, msg)
        self.assertIsNone(result.default, msg)

    @setup_django
    def test_init_from_db(self):
        """Test MemoryModel.from_db method."""
        result = self.TestModel.from_db({'id': 1, 'default': ''})
        self.assertEqual(result.id, 1)
        self.assertEqual(result.pk, 1)
        self.assertIsNone(result.value)
        self.assertEqual(result.default, 2)

        self.assertRaisesRegex(
            ValidationError, expected_error_fmt % 'text', self.TestModel.from_db, {'value': 'text'}
        )

    @setup_django
    def test_check_data(self):
        """Test MemoryModel.check_data method."""
        with self.subTest('Invalid data types'):
            result = self.TestModel.check_data({'id': -1, 'value': 'text', 'default': None})

            self.assertListEqual(
                result, [
                    Error(
                        msg='Invalid value',
                        hint='Ensure this value is greater than or equal to 0.',
                        obj='column id',
                        id='memory_db.models.E002'
                    ),
                    Error(
                        msg='Invalid value',
                        hint=expected_error_fmt % 'text',
                        obj='column value',
                        id='memory_db.models.E002'
                    ),
                    Error(
                        msg='Invalid value',
                        hint='This field cannot be null.',
                        obj='column default',
                        id='memory_db.models.E002'
                    )
                ]
            )

        with self.subTest('Invalid blank data'):
            result = self.TestModel.check_data({'id': '', 'value': '', 'default': ''})
            self.assertListEqual(
                result, [
                    Error(
                        msg='Invalid value',
                        hint=expected_error_fmt % '',
                        obj='column id',
                        id='memory_db.models.E002'
                    ),
                ]
            )

        with self.subTest('Unset data'):
            result = self.TestModel.check_data({})
            self.assertListEqual(
                result, [
                    Error(
                        msg='Missing field', hint=None, obj='column id', id='memory_db.models.E001'
                    ),
                    Error(
                        msg='Missing field',
                        hint=None,
                        obj='column value',
                        id='memory_db.models.E001'
                    ),
                    Error(
                        msg='Missing field',
                        hint=None,
                        obj='column default',
                        id='memory_db.models.E001'
                    ),
                ]
            )

    def test_hashable(self):
        """Test Model.__hash__ method."""
        result1 = hash(self.TestModel(id=1))
        result2 = hash(self.TestModel(id=1))
        result3 = hash(self.TestModel(id=3))

        self.assertEqual(result1, result2)
        self.assertNotEqual(result1, result3)

        dict_ = {result1: True}

        self.assertIn(
            result2, dict_, 'result1 and result2 are identicals, result2 should be find in the dict'
        )
