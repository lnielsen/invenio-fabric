# -*- coding: utf-8 -*-
#
# A Fabric file for installing, deploying and running Invenio on CERN
# SLC5/6 hosts.
#
# Lars Holm Nielsen <lars.holm.nielsen@cern.ch>
#
# Copyright (C) 2012 CERN.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.


from setuptools import setup, find_packages

setup(
    name='invenio-fabric',
    version='0.1',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=False,
    zip_safe=False,
    install_requires=['distribute', 'Fabric>=1.4','Jinja2' ],

    author='Lars Holm Nielsen',
    author_email='lars.holm.nielsen@cern.ch',
    description='Fabric tasks for installing, deploying and running Invenio on CERN SLC5/6 hosts.',
    license="GPL",
    keywords="invenio fabric cern",
    url="https://github.com/lnielsen-cern/invenio-fabric"
)
