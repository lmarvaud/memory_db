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

from memory_db.utils import cast_value


class TestCastValue(TestCase):
    """Test cast_value util."""

    def test(self):
        """
        Test cast_value util.

        Tests contains: the value, the value to cast, the expected result
        """
        tests = (
            (int(), '1', 1.0),
            (int(), 'Not digit', 'Not digit'),
            (float(), '2.0', 2.0),
            (float(), 'Not digit', 'Not digit'),
            (bool(), 'True', True),
            (bool(), '1', True),
            (bool(), 'False', False),
            (bool(), 'anything else', False),
            (bool(), True, True),
            (bool(), 1, 1),
            (str(), 1, '1'),
            (str(), 2.0, '2.0'),
        )

        for value, filter_value, expected_result in tests:
            with self.subTest(
                value=value, filter_value=filter_value, expected_result=expected_result
            ):
                result = cast_value(value, filter_value)
                self.assertEqual(result, expected_result)
                self.assertIsInstance(result, type(expected_result))
