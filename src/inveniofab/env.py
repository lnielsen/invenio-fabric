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
Fabric tasks for defining environments. Specifically it will setup default
values, as well as allow loading an environment without activating it (useful
if you want to say copy a database from production to integration, and thus
needs access to both environments at the same time.
"""

from fabric.api import execute, abort, task
from fabric import state
from fabric.api import task, abort
from jinja2 import Environment, FileSystemLoader
import copy
import os

def env_create(envname, defaults_func=None, activate=True, **kwargs):
    """
    Create a new environment (e.g. integration, production,
    local). Minimal usage::

      @task
      def prod(activate=True, **kwargs)
          env = env_create('prod', activate=activate, **kwargs)

          env.CFG_
          return env

    @param envname: str, Name of environment (must be same as task envname).
    @param defaults_func: callable taking a dictionary as argument and returns
        the same dictionary. Used to setup defaults in the environment.
    @param activate: Bool, True to activate the environment, or False to just
        load (i.e. put config vars in fabric.api.env or not)
    """
    from fabric.api import env

    if activate:
        some_env = env
        some_env.env_active = True
    else:
        tmp = env.jinja
        env.jinja = None

        some_env = copy.deepcopy(env)
        some_env.env_active = False

        env.jinja = tmp

    some_env.env_name = envname

    # Allow user to setup defaults
    if defaults_func:
        some_env = defaults_func(some_env, **kwargs)
    else:
        some_env = env_defaults(some_env, **kwargs)

    return some_env


def env_get(name):
    """
    Get environment by name (does not activate the environment).

    An environment is defined in a local task. This task will
    look for a task with the name <name> and execute. Hence
    the task defining the environment.
    """
    from fabric.api import env

    # Check if active env is requested
    if env.get('env_active', False) and env.get('env_name', None) == name:
        return env

    if 'loaded_envs' not in env:
        env.loaded_envs = {}

    # Check if env is already loaded, if not load it.
    if name not in env.loaded_envs:
        res = execute(name, activate=False)
        env.loaded_envs[name] = res['<local-only>']

    return env.loaded_envs[name]


def env_defaults(env, name='invenio', prefix=None, **kwargs):
    """
    Setup defaults in environment.

    Note: This can be overridden by the user.
    """
    # Initialise template loader
    env.jinja = Environment(loader=FileSystemLoader([env.env_name, 'common']))
    prefix = prefix or os.path.join(os.getenv('WORKON_HOME', '/opt'), name)

    env.roledefs = {
        'web': [],
        'lb': [],
        'db-master': [],
        'db-slave': [],
        'workers': [],
    }

    env.update({
        'REQUIREMENTS': ['requirements.txt', 'requirements-extra.txt', ],
        'WITH_VIRTUALENV': True,
        'WITH_DEVSERVER': True,
        'WITH_WORKDIR': True,
        'WITH_DEVSCRIPTS': True,
        'PYTHON': kwargs.get('python', 'python'),
        'ACTIVATE': '. %(CFG_INVENIO_PREFIX)s/bin/activate',
        'CFG_INVENIO_REPOS': [],
        'CFG_INVENIO_CONF': None,
        'CFG_INVENIO_SRCDIR': os.path.join(prefix, 'src/invenio'),
        'CFG_INVENIO_PREFIX': prefix,
        'CFG_SRCDIR' : os.environ.get('CFG_SRCDIR', os.path.join(prefix, 'src')),
        'CFG_SRCWORKDIR' : os.path.join(prefix, 'src'),
        'CFG_INVENIO_HOSTNAME': "localhost",
        'CFG_INVENIO_DOMAINNAME': "",
        'CFG_INVENIO_PORT_HTTP': "4000",
        'CFG_INVENIO_PORT_HTTPS': "4000",
        'CFG_INVENIO_USER': env.user,
        'CFG_INVENIO_APACHECTL': '/etc/init.d/httpd',
        'CFG_INVENIO_ADMIN': 'nobody@localhost',

        'CFG_DATABASE_DUMPDIR': prefix,
        'CFG_DATABASE_HOST': 'localhost',
        'CFG_DATABASE_PORT': 3306,
        'CFG_DATABASE_NAME': name,
        'CFG_DATABASE_USER': name,
        'CFG_DATABASE_PASS': 'my123p$ss',
        'CFG_DATABASE_DROP_ALLOWED': True,

        # FIXME: Set to localhost or leave empty?
        'CFG_MISCUTIL_SMTP_HOST': '127.0.0.1',
        'CFG_MISCUTIL_SMTP_PORT': '1025',
    })

    env.CFG_INVENIO_REPOS = [
        ('invenio', {
            'repository' : 'http://invenio-software.org/repo/invenio/',
            'ref': 'origin/master',
            'bootstrap_targets': ['all', 'install', 'install-mathjax-plugin', 'install-ckeditor-plugin', 'install-pdfa-helper-files', 'install-jquery-plugins', ],
            'deploy_targets': ['all', 'check-upgrade', 'install', ],
        }),
    ]

    return env

#
# Helper tasks
# 
