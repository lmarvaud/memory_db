#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
import glob
from typing import List

from setuptools import find_packages, setup

packages = find_packages(exclude=('tests', 'docs', 'venv'))


def find_stub_files(package: str) -> List[str]:
    """Find stub files in package."""
    result = glob.glob1(package, '*.pyi') + glob.glob1(package, 'py.typed')
    return result


with open('README.md', 'r') as f:
    long_description = f.read()

with open('LICENSE', 'r') as f:
    license_ = f.read()

setup(
    name='memory_db',
    version='1.0.0',
    description='Django like model in memory',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Leni Marvaud',
    license=license_,
    packages=packages,
    package_data={package: find_stub_files(package)
                  for package in packages},
    classifiers=[
        'Programming Language :: Python :: 3.6',
        'Operating System :: OS Independent',
    ],
    install_requires=[
        'Django>3,<4',
        'cached_property>1,<2',
    ]
)
