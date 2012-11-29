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
"""

from fabric.api import task, abort
from fabric.colors import red
from inveniofab.api import *
import os

@task
def loc(activate=True):
    """
    Local environment

    The other included examples normally uses a combination of env_create,
    env_make_name and env_override to automatically set all the environment
    variables based on parameters such as Python interpreter, branch etc.

    This example shows which variables are being set, to make demystify what
    the automatic guessing is doing.
    """
    prefix = "/opt/atlantis"

    # 1. Make call to env_create as the first thing.
    env = env_create('loc', activate=activate)

    # 2. Set hosts for defind roles
    env.roledefs = {
        'web': [],
        'lb': [],
        'db-master': [],
        'db-slave': [],
        'workers': [],
    }

    # 3. Set env variables
    env.WITH_VIRTUALENV =  True
    env.WITH_DEVSERVER =  True
    env.WITH_WORKDIR =  True
    env.WITH_DEVSCRIPTS =  True
    env.PYTHON =  'python'
    env.ACTIVATE =  '. %(CFG_INVENIO_PREFIX)s/bin/activate'
    env.CFG_INVENIO_CONF =  None
    env.CFG_INVENIO_PREFIX =  prefix
    env.CFG_INVENIO_SRCDIR = os.path.join(prefix, 'src/invenio')
    env.CFG_INVENIO_REPOS = [
        ('invenio', {
            'repository' : 'http://invenio-software.org/repo/invenio/',
            'ref': 'master',
            'bootstrap_targets': ['all', 'install', 'install-mathjax-plugin',
                        'install-ckeditor-plugin', 'install-pdfa-helper-files',
                        'install-jquery-plugins', ],
            'deploy_targets': ['all', 'check-upgrade', 'install', ],
            'requirements': ['requirements.txt', 'requirements-extra.txt', ],
        }),
    ]
    env.CFG_SRCDIR = os.path.join(prefix, 'src')
    env.CFG_SRCWORKDIR = os.path.join(prefix, 'src')
    env.CFG_INVENIO_HOSTNAME =  "localhost"
    env.CFG_INVENIO_DOMAINNAME =  ""
    env.CFG_INVENIO_PORT_HTTP =  "4000"
    env.CFG_INVENIO_PORT_HTTPS =  "4000"
    env.CFG_INVENIO_USER =  env.user
    env.CFG_INVENIO_APACHECTL =  '/etc/init.d/httpd'
    env.CFG_INVENIO_ADMIN =  'nobody@localhost'

    env.CFG_DATABASE_DUMPDIR =  prefix
    env.CFG_DATABASE_HOST =  'localhost'
    env.CFG_DATABASE_PORT =  3306
    env.CFG_DATABASE_NAME =  'atlantis_loc'
    env.CFG_DATABASE_USER =  'atlantis_loc'
    env.CFG_DATABASE_PASS =  'my123p$ss'
    env.CFG_DATABASE_DROP_ALLOWED =  True

    env.CFG_MISCUTIL_SMTP_HOST =  '127.0.0.1'
    env.CFG_MISCUTIL_SMTP_PORT =  '1025'

    env.CFG_INSPIRE_SITE = False

    # 4. Return env
    return env