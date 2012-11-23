# -*- coding: utf-8 -*-
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
    version='0.2.5',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=False,
    zip_safe=False,
    install_requires=['distribute', 'Fabric>=1.4', 'Jinja2', 'virtualenvwrapper','Sphinx'],
    data_files=[
        ('share/atlantis/',[
            'examples/atlantis/fabfile.py',
            'examples/atlantis/fabfile_minimal.py',
        ]),
        ('share/atlantis/common/',[
            'examples/atlantis/common/activate-profile.tpl',
            'examples/atlantis/common/requirements.txt',
            'examples/atlantis/common/requirements-extra.txt',
            'examples/atlantis/common/rundevserver.py.tpl',
        ]),
        ('share/openaire/',[
            'examples/openaire/fabfile.py',
        ]),
        ('share/openaire/common/',[
            'examples/openaire/common/activate-profile.tpl',
            'examples/openaire/common/config_local.py.tpl',
            'examples/openaire/common/requirements.txt',
            'examples/openaire/common/requirements-extra.txt',
            'examples/openaire/common/rundevserver.py.tpl',
        ]),
        ('share/openaire/common/etc/',[
            'examples/openaire/common/etc/invenio-local.conf',
        ]),
        ('share/openaire/int/etc/',[
            'examples/openaire/int/etc/invenio-local.conf',
        ]),
        ('share/inspire/',[
            'examples/inspire/fabfile.py',
        ]),
        ('share/inspire/common/',[
            'examples/inspire/common/activate-profile.tpl',
            'examples/inspire/common/config_local.py.tpl',
            'examples/inspire/common/config-local.mk',
            'examples/inspire/common/requirements.txt',
            'examples/inspire/common/requirements-extra.txt',
            'examples/inspire/common/rundevserver.py.tpl',
        ]),
        ('share/inspire/common/etc/',[
            'examples/inspire/common/etc/invenio-local.conf',
        ]),
    ],

    author='CERN',
    author_email='info@invenio-software.org',
    description='Fabric tasks for working with Invenio repository software',
    license="GPL",
    keywords="invenio fabric CERN",
    url="https://github.com/lnielsen-cern/invenio-fabric",
)
