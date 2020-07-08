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


def cast_value(value, filter_value):
    """Cast the filter value to be comparable to the value.

    todo: cast according to a mapper not the value type
    """
    if isinstance(filter_value, str) and isinstance(value, bool):
        filter_value = filter_value.lower() in ('true', '1')
    elif isinstance(filter_value, str) and \
            isinstance(value, (int, float)):
        try:
            filter_value = float(filter_value)
        except ValueError:
            pass
    elif isinstance(value, str) and not isinstance(filter_value, str):
        filter_value = str(filter_value)
    return filter_value
