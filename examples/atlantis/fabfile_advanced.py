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

Setup virtual environment and database with Python 2.4 and Invenio 1.0.0:
  fab loc:py=2.4,ref=master bootstrap
  fab loc:py=2.4,ref=master invenio_create_demosite

Dump (database and virtual environment), load and drop:
  fab loc:py=2.4,ref=master dump
  fab loc:py=2.4,ref=master load
  fab loc:py=2.4,ref=master drop
"""

from fabric.api import task, abort
from fabric.colors import red
from inveniofab.api import *
import os

PYTHON_VERSIONS = {
    '2.7' : os.path.expanduser('~/.pythonbrew/pythons/Python-2.7.3/bin/python'),
    '2.6' : os.path.expanduser('~/.pythonbrew/pythons/Python-2.6.7/bin/python'),
    '2.5' : os.path.expanduser('~/.pythonbrew/pythons/Python-2.5.4/bin/python'),
    '2.4' : os.path.expanduser('~/.pythonbrew/pythons/Python-2.4.6/bin/python'),
}

REFS = {
    'jkuncar-public/flask' : {
        'bootstrap_targets': ['all', 'install', 'install-mathjax-plugin', 'install-ckeditor-plugin', 'install-pdfa-helper-files', 'install-jquery-plugins', 'install-jquery-tokeninput', 'install-bootstrap' ],
        'deploy_targets': ['all', 'check-upgrade', 'install', ],
        'requirements' : ['%(CFG_INVENIO_SRCDIR)s/requirements.txt', '%(CFG_INVENIO_SRCDIR)s/requirements-extras.txt', '%(CFG_INVENIO_SRCDIR)s/requirements-flask.txt', '%(CFG_INVENIO_SRCDIR)s/requirements-flask-ext.txt',],
    },
    'origin/v0.99.0' : {
        'bootstrap_targets' : ['all', 'install'],
        'deploy_targets' : ['all', 'install'],
    },
    'origin/v0.99.5' : {
        'bootstrap_targets' : ['all', 'install'],
        'deploy_targets' : ['all', 'install'],
    },
}



@task
def loc(activate=True, py=None, ref=None, **kwargs):
    """
    Local environment (example: loc:py=2.4,ref=maint-1.1)
    """
    if py is None:
        kwargs['python'] = 'python'
    elif py in PYTHON_VERSIONS:
        kwargs['python'] = PYTHON_VERSIONS[py]
    else:
        abort(red("Unknown Python version %s" % py))

    env = env_create('loc', name=make_name(py or '', ref or ''),
                     activate=activate, **kwargs)

    env.APACHECTL = 'service apache2'

    # Override make targets and requirements for specific branches
    if ref in REFS:
        env.CFG_INVENIO_REPOS[0][1]['ref'] = ref
        if 'bootstrap_targets' in REFS[ref]:
            env.CFG_INVENIO_REPOS[0][1]['bootstrap_targets'] = REFS[ref]['bootstrap_targets']
        if 'deploy_targets' in REFS[ref]:
            env.CFG_INVENIO_REPOS[0][1]['deploy_targets'] = REFS[ref]['deploy_targets']
        if 'requirements' in REFS[ref]:
            env.REQUIREMENTS = REFS[ref]['requirements']

#
# Helpers
#
def make_name(python, ref):
    ref = ref.split("/")
    ref = ref[-1].replace("-","_")
    python = python.replace(".","")

    name = "atlantis%s%s" % (python, ref)
    if len(name) > 16:
        name = name.replace("_", "", len(name) - 16)
        return name[:16]

    return name
