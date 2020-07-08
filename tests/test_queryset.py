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
from typing import Any, Dict, List, NamedTuple, Optional
from unittest import skip, TestCase

from django.core.exceptions import FieldDoesNotExist, MultipleObjectsReturned

from tests.models import TestMemoryModel


class FilterTest(NamedTuple):
    """TestFilter valid test case."""

    result: List[TestMemoryModel]
    filter_: Optional[Dict[str, Any]] = None
    exclude: Optional[Dict[str, Any]] = None


class FilterTestError(NamedTuple):
    """TestFilter invalid test case."""

    error: Exception
    filter_: Optional[Dict[str, Any]] = None
    exclude: Optional[Dict[str, Any]] = None


one = TestMemoryModel(pk=1, value='One')
two = TestMemoryModel(pk=2, value='Two')
three = TestMemoryModel(pk=3, value='Three')


class TestFilter(TestCase):
    """Filter test case."""

    def test(self):
        """Run tests on filter."""
        tests = [
            FilterTest([one, two, three], filter_={}),
            FilterTest([one, two, three], exclude={}),
            FilterTest([one], filter_={'pk': 1}),
            FilterTest([one], filter_={'pk': '1'}),
            FilterTest([one], filter_={'value': 'One'}),
            FilterTest([one], exclude={'pk__in': [2, 3]}),
            FilterTest([one, two], filter_={'pk__in': [1, 2]}),
            FilterTest([one, two], filter_={'value__in': ['One', 'Two']}),
            FilterTestError(FieldDoesNotExist, filter_={'invalid': 1}),
            FilterTest([two], filter_={'pk__lte': 2}, exclude={'pk__lt': 2}),
            FilterTest([two, three], filter_={'pk__gte': 2}),
            FilterTest([three], filter_={'pk__gt': 2}),
            FilterTest([one], filter_={'value__contains': 'O'}),
            FilterTest([one, two], filter_={'value__icontains': 'O'}),
            FilterTest([one, two, three], filter_={'value__isnull': False}),
        ]
        for test in tests:
            with self.subTest(filter=test.filter_, exclude=test.exclude):
                result = TestMemoryModel.objects
                if test.filter_ is not None:
                    result = result.filter(**test.filter_)
                if test.exclude is not None:
                    result = result.exclude(**test.exclude)
                if isinstance(test, FilterTest):
                    self.assertListEqual(list(result), test.result)
                elif isinstance(test, FilterTestError):
                    with self.assertRaises(test.error):
                        list(result)

    @skip('feature: make copy of each queryset, to use them later')
    def test_chain_filters(self):
        """Test multiple filters."""
        result_all = TestMemoryModel.objects.all()
        result_filter1 = result_all.filter(pk__lte=2)
        result_filter2 = result_filter1.exclude(pk__lt=2)

        self.assertEqual(len(result_filter2), 1)
        self.assertEqual(len(result_filter1), 2)
        self.assertEqual(len(result_all), 3)

        result_all = TestMemoryModel.objects.all()
        result_filter1 = result_all.filter(pk__lte=2)
        result_filter2 = result_filter1.exclude(pk__lt=2)

        self.assertEqual(len(result_all), 3)
        self.assertEqual(len(result_filter1), 2)
        self.assertEqual(len(result_filter2), 1)


class TestGetItem(TestCase):
    """Test getMemoryQuerySet __get_item__ method."""

    def test_get_one(self):
        """Test get_item."""
        tests = [
            (0, one),
            (1, two),
            (2, three),
            (-1, three),
            (-2, two),
            (-3, one),
            ('0', one),
        ]
        queryset = TestMemoryModel.objects.all()
        for item, expected_result in tests:
            with self.subTest(get_item=item):
                result = queryset[item]
                self.assertEqual(result, expected_result)

    def test_get_one_out_of_range(self):
        """Test get_item out of range."""
        tests = [3, -4]
        queryset = TestMemoryModel.objects.all()
        for item in tests:
            with self.subTest(get_item=item):
                with self.assertRaises(TestMemoryModel.DoesNotExist):
                    queryset[item]

    def test_get_slice(self):
        """Test get_item with slice."""
        tests = [
            (slice(0, 0), []),
            (slice(0, 1), [one]),
            (slice(0, 2), [one, two]),
            (slice(-1, 0), [three]),
            (slice(-2, 0), [two, three]),
            (slice(-3, -1), [one, two]),
        ]
        for slice_, expected_result in tests:
            with self.subTest(get_item=slice_):
                result = TestMemoryModel.objects.all()[slice_]
                self.assertEqual(result, expected_result)

    def test_get_slice_out_of_range(self):
        """Test get_item with slice out of the range."""
        tests = [
            slice(3, 4),
            slice(-4, -3),
        ]
        for slice_ in tests:
            with self.subTest(get_item=slice_):
                result = TestMemoryModel.objects.all()[slice_]
                self.assertEqual(result, [])


class TestContain(TestCase):
    """Test MemoryQuerySet contains methods."""

    def test_in(self):
        """Test MemoryQuerySet `in` builtin."""
        self.assertIn(one, TestMemoryModel.objects.filter(pk=1))
        self.assertNotIn(two, TestMemoryModel.objects.filter(pk=1))

    def test_exists(self):
        """Test MemoryQuerySet exists method."""
        self.assertTrue(TestMemoryModel.objects.filter(pk=1).exists())
        self.assertFalse(TestMemoryModel.objects.filter(pk=0).exists())


class TestOrder(TestCase):
    """Test MemoryQuerySet ordering methods."""

    def test_reversed(self):
        """Test reversed(MemoryQuerySet) method."""
        self.assertEqual(reversed(TestMemoryModel.objects.all()), [three, two, one])
        self.assertEqual(reversed(TestMemoryModel.objects.filter(pk__lte=2)), [two, one])
        self.assertEqual(reversed(TestMemoryModel.objects.exclude(pk__lte=2)), [three])

    def test_order_by(self):
        """Test MemoryQuerySet.order_by method."""
        self.assertEqual(
            TestMemoryModel.objects.order_by('value'),
            reversed(TestMemoryModel.objects.order_by('-value'))
        )
        self.assertEqual(TestMemoryModel.objects.order_by('value'), [one, three, two])
        self.assertEqual(TestMemoryModel.objects.order_by('-value'), [two, three, one])
        self.assertEqual(TestMemoryModel.objects.order_by('pk', '-value'), [one, two, three])

    def test_ordered(self):
        """Test MemoryQuerySet.ordered property."""
        self.assertFalse(TestMemoryModel.objects.all().ordered)
        self.assertTrue(TestMemoryModel.objects.order_by('pk').ordered)
        self.assertTrue(reversed(TestMemoryModel.objects.all()).ordered)


class TestValues(TestCase):
    """Test MemoryQuerySet values methods."""

    def test_values(self):
        """Test MemoryQuerySet.values method."""
        expected_result = {'id': 1, 'value': 'One'}

        result = TestMemoryModel.objects.values('id', 'value').get(pk=1)

        self.assertEqual(result, expected_result)

        result = TestMemoryModel.objects.values('id', 'value').filter(pk=1)

        self.assertEqual(result, [expected_result])

    def test_values_list(self):
        """Test MemoryQuerySet.values_list method."""
        expected_result = (1, 'One')

        result = TestMemoryModel.objects.values_list('id', 'value').get(pk=1)

        self.assertEqual(result, expected_result)

        result = TestMemoryModel.objects.values_list('id', 'value').filter(pk=1)

        self.assertEqual(result, [expected_result])

    def test_values_list_flat(self):
        """Test MemoryQuerySet.values_list(flat=True) method."""
        expected_result = 'One'

        result = TestMemoryModel.objects.values_list('value', flat=True).get(pk=1)

        self.assertEqual(result, expected_result)

        result = TestMemoryModel.objects.values_list('value', flat=True).filter(pk=1)

        self.assertEqual(result, [expected_result])


class TestGetters(TestCase):
    """Test MemoryQuerySet getters."""

    def test_get(self):
        """Test MemoryQuerySet.get method."""
        with self.assertRaises(MultipleObjectsReturned):
            TestMemoryModel.objects.get()
        with self.assertRaises(MultipleObjectsReturned):
            TestMemoryModel.objects.filter(pk__in=[1, 2]).get()
        result1 = TestMemoryModel.objects.filter(pk__in=[1, 2]).exclude(pk=1).get()
        result2 = TestMemoryModel.objects.filter(pk=3).get()

        self.assertEqual(result1, two)
        self.assertEqual(result2, three)

    def test_first(self):
        """Test MemoryQuerySet.first method."""
        result1 = TestMemoryModel.objects.first()
        result2 = TestMemoryModel.objects.exclude(pk=1).first()
        result3 = TestMemoryModel.objects.filter(pk=3).first()

        self.assertEqual(result1, one)
        self.assertEqual(result2, two)
        self.assertEqual(result3, three)

    def test_last(self):
        """Test MemoryQuerySet.last method."""
        result1 = TestMemoryModel.objects.last()
        result2 = TestMemoryModel.objects.exclude(pk=3).last()
        result3 = TestMemoryModel.objects.filter(pk=1).last()

        self.assertEqual(result1, three)
        self.assertEqual(result2, two)
        self.assertEqual(result3, one)
