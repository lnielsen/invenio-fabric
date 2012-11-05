# -*- coding: utf-8 -*-
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

"""
Fabric tasks for bootstrapping, installing, deploying and running Atlantis.

Examples
--------
Setup virtual environment and database with Python 2.4 and Invenio v1.1.0:
  fab loc:py=24,ref=origin/v1.1.0 bootstrap
  fab loc:py=24,ref=origin/v1.1.0 invenio_create_demosite

Dump, load and drop (database and virtual environment):
  fab loc:py=27,ref=master dump
  fab loc:py=27,ref=master load
  fab loc:py=27,ref=master drop

Requirements:
 * pythonbrew must be installed to specify a specific Python version.
"""

from fabric.api import task, abort
from fabric.colors import red
from inveniofab.api import *
import os

REF_OVERRIDE = {
    'invenio' : {
        'flask' : {
            'bootstrap_targets': ['all', 'install', 'install-mathjax-plugin',
                'install-ckeditor-plugin', 'install-pdfa-helper-files',
                'install-jquery-plugins', 'install-jquery-tokeninput',
                'install-bootstrap' ],
            'deploy_targets': ['all', 'check-upgrade', 'install', ],
            'requirements' : ['%(CFG_INVENIO_SRCDIR)s/requirements.txt', 
                '%(CFG_INVENIO_SRCDIR)s/requirements-extras.txt',
                '%(CFG_INVENIO_SRCDIR)s/requirements-flask.txt',
                '%(CFG_INVENIO_SRCDIR)s/requirements-flask-ext.txt',],
        },
        'origin/v0.99.0' : {
            'bootstrap_targets' : ['all', 'install'],
            'deploy_targets' : ['all', 'install'],
        },
        'origin/v0.99.5' : {
            'bootstrap_targets' : ['all', 'install'],
            'deploy_targets' : ['all', 'install'],
        },
    },
}
"""
Overrides installation procedure for a specific branch.

Certain branches might have special installation requirements which does not
match the default. This dictionary allows you to override the default values.
"""


@task
def loc(activate=True, py=None, ref=None, **kwargs):
    """
    Local environment (example: loc:py=24,ref=maint-1.1)
    """
    env = env_create('loc', name=env_make_name('atlantis', py or '', ref or ''),
                     activate=activate, python=py, **kwargs)

    return env_override(env, 'invenio', ref, global_overrides=REF_OVERRIDE)
