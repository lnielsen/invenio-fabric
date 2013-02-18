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


@task
def loc(activate=True, py=None, ref=None, **kwargs):
    """
    Local environment (example: loc:py=24,ref=maint-1.1)
    """
    if 'name' not in kwargs:
        kwargs['name'] = env_make_name('atlantis', py or '', ref or '')

    env = env_create('loc', activate=activate, python=py, **kwargs)

    return env_override(env, 'invenio', ref, {'ref': ref})


@task
def int(activate=True, **kwargs):
    """ Environment: Integration """
    env = env_create('int', activate=activate, **kwargs)

    env.roledefs = {
        'web': ['pccis92.cern.ch', ],
        'lb': [],
        'db-master': ['pccis92.cern.ch', ],
        'db-slave': [],
        'workers': ['pccis92.cern.ch', ],
    }

    env.CFG_SRCDIR = '/opt/cdsweb/src'
    env.CFG_INVENIO_SRCDIR = os.path.join(env.CFG_SRCDIR, 'invenio')
    env.CFG_INVENIO_PREFIX = '/opt/cdsweb'
    env.CFG_INVENIO_CONF = 'etc/invenio-local.conf'
    env.CFG_INVENIO_HOSTNAME = "pccis82"
    env.CFG_INVENIO_DOMAINNAME = ".cern.ch"
    env.CFG_INVENIO_PORT_HTTP = "80"
    env.CFG_INVENIO_PORT_HTTPS = "443"
    env.CFG_INVENIO_USER = 'apache'
    env.CFG_INVENIO_APACHECTL = '/etc/init.d/httpd'
    env.CFG_INVENIO_ADMIN = 'cds-admin@cern.ch'

    #env.CFG_FILES = {
    #    'web': [
    #        'etc/certs/zenodo-dev.cern.ch.crt',
    #        'etc/certs/zenodo-dev.cern.ch.key',
    #    ]
    #}

    env.CFG_INVENIO_REPOS = [
        ('invenio', {
            'repository': 'http://invenio-software.org/repo/invenio/',
            'ref': 'origin/next',
            'bootstrap_targets': ['all', 'install', 'install-mathjax-plugin', 'install-ckeditor-plugin', 'install-pdfa-helper-files', 'install-jquery-plugins', 'install-bootstrap', 'install-plupload-plugin', ],
            'deploy_targets': ['all', 'install', ],
            'requirements': ['%(CFG_INVENIO_SRCDIR)s/requirements.txt',
                '%(CFG_INVENIO_SRCDIR)s/requirements-extras.txt',
                '%(CFG_INVENIO_SRCDIR)s/requirements-flask.txt',
                '%(CFG_INVENIO_SRCDIR)s/requirements-flask-ext.txt', ],
        }),
        # ('openaire', {
        #     'repository': 'https://github.com/Zenodo/zenodo.git',
        #     'ref': 'origin/next',
        #     'bootstrap_targets': ['all', 'install', ],
        #     'deploy_targets': ['all', 'install', ],
        #     'requirements': ['%(CFG_OPENAIRE_SRCDIR)s/requirements.txt'],
        # }),
    ]

    env.CFG_DATABASE_DUMPDIR = env.CFG_INVENIO_PREFIX
    env.CFG_DATABASE_HOST = 'localhost'
    env.CFG_DATABASE_PORT = 3306
    env.CFG_DATABASE_NAME = 'cds'
    env.CFG_DATABASE_USER = 'cds'
    env.CFG_DATABASE_PASS = 'blabla'
    env.CFG_DATABASE_DROP_ALLOWED = True

    env.WITH_WORKDIR = False
