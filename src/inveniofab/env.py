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
Fabric tasks for defining environments.

Fabric environment dictionary
---------------------------
An integral part of Fabric is what is know as "environments": a Python dictionary
subclass which is used as a combination settings registry and shared inter-task
data namespace. Most of Fabric's and Invenio Fabrics behaviour is modifiable 
through env variables.

The environment is accessible through ``fabric.api.env``, and allows e.g. a task
access to the current user etc (``user`` is called an env variable)::

  from fabric.api import env
  @task
  def sometask():
      print env.user
      print env.host

For more information on Fabric environment dictionary please see 
http://fabric.readthedocs.org/en/latest/usage/env.html

Invenio Fabric environments
---------------------------
The tasks in this module helps you define the env variables which all other
Invenio Fabric tasks depends on. Secondly, it provide means for loading 
env variables, but without putting them in ``fabric.api.env``. This is useful
for tasks like ``fab int mysql_copy:prod`` which would copy the database from
production to integration, and thus need access to host, user, password etc from
both the integration and production environment at the same time. 

Usage
^^^^^
Defining a new environment is simple::

  from fabric.api import task
  from inveniofab.api import *

  @task
  def prod(activate=True):
      # Step 1: Create env with default values
      env = env_create('prod', activate=activate)

      # Step 2: Modify some values
      env.CFG_XYZ = ...

      # Step 3: Return env
      return env

Things to note:

 * The task must take a keyword argument ``activate`` which defaults to ``True``.
   This is used to control if the environment is activated or not (i.e. copied
   to ``fabric.api.env``.
 * First parameter to :meth:`~env_create`, must match the task name (``prod`` in
   this case). Otherwise the environment cannot be loaded without activating it,
   and template overriding will not work properly (see later in this chapter).
 * You must return the environment variable at the end of the task.

Running tasks
^^^^^^^^^^^^^
As mentioned above, the Invenio Fabric tasks depends on an environment being
defined. The pattern to run Invenio Fabric task is::

  fab <env> <task1> <task2>

In the example above, you could for instance run::

  fab prod bootstrap

to bootstrap the production environment. I.e. you always call an environment 
task as the first task.

Also note, that some task takes parameters::

  fab <env> <task1>:<arg1>,<arg2>,<kw1>=<val>,<kw2>=<val> <task2> ...
  fab prod bootstrap:quite=1

Roles
^^^^^
By default the following roles are defined:

 * ``web`` - frontend webservers
 * ``lb`` - load balancers
 * ``db-master`` - master databases
 * ``db-slave`` - slave databases
 * ``workers`` - worker nodes

Some task will use these roles to decide which machine to execute a given 
command on. For more on Fabric roles please see 
http://fabric.readthedocs.org/en/1.4.3/usage/execution.html#roles

You may override these roles in your environment task::

  @task
  def prod(activate=True):
      env = env_create('prod', activate=activate)
      env.roledefs['web'] = [...]
      return env 

Creating tasks
--------------
When creating task you can access the variables simply by loading the Fabric
env dictionary from ``fabric.api.env``. All Invenio Fabric env variables are 
upper-case (for now, please look in the source code of :meth:`~env_defaults` to 
see, which variables are defined).

Example::

  from fabric.api import env

  @task
  def sometask():
      print env.CFG_INVENIO_PREFIX
      local("%(CFG_INVENIO_PREFIX)s/bin/python" % env)


Template loading
^^^^^^^^^^^^^^^^
The Invenio Fabric environment by default also configures a Jinja2 environment
which can be used to load and render templates.

Example::

  from fabric.api import env

  @task
  def sometask():
      tpl = env.jinja.get_template("etc/invenio-local.conf")
      output = tpl.render(env)
      ...

Above code will look for the template first in ``<env>/etc/invenio-local.conf``,
then ``common/etc/invenio-local.conf``. So assuming your directory structure
looks like below::

  fabfile.py
  common/etc/invenio-local.conf
  int/etc/invenio-local.conf

Running ``fab int sometask`` would use the template 
``int/etc/invenio-local.conf``, while ``fab prod sometask`` and 
``fab loc sometask`` would use the template ``common/etc/invenio-local.conf``.

This allows you to define common templates for configuration files, and 
selectively override them for certain environments if needed.


Relation to invenio-local.conf
------------------------------
Many variables map directly to their Invenio counterpart - e.g.
``CFG_DATABASE_NAME`` can be defined in invenio-local.conf as well as in
Invenio Fabric ``env.CFG_DATABASE_NAME``.

Usually when deploying or working with a specific Invenio project, some 
configuration variables depend only on the project (e.g. 
``CFG_WEBSTYLE_TEMPLATE_SKIN``), while others depend
on the deployment environment (e.g. ``CFG_DATABASE_HOST``).

As a general rule, project-wide configuration should go in a common 
``invenio-local.conf`` template, while deployment dependent configuration should
be defined in a Fabric environment task. The ``invenio-local.conf`` can then be
render with the Fabric env variables.

Tasks
-----
"""

from fabric import state
from fabric.api import execute, abort, task
from fabric.api import task, abort
from inveniofab.utils import pythonbrew_versions
from jinja2 import Environment, FileSystemLoader
import copy
import os

GLOBAL_REFS_OVERRIDE = {
    'invenio' : {
        'next' : {
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


def env_create(envname, defaults_func=None, activate=True, **kwargs):
    """
    Setup a new environment (e.g. integration, production, local).
    
    See module documentation above for detailed explanation of enviroments.
    
    :param envname: str, Name of environment (must be same as task envname).
    :param defaults_func: callable taking a dictionary as argument and returns
        the same dictionary. Used to setup defaults in the environment. By 
        default the :meth:`~env_defaults` is used. Take great care if overriding
        this, since many tasks expects specific variables to be defined.
    :param activate: True to activate the environment, or False to just
        load it (i.e. should config be put in ``fabric.api.env`` or not).
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
    
    Example::
    
        from fabric.api import env

        @task
        def sometask():
            another_env = env_get('prod')
            print env.CFG_SITE_URL
            print another_env.CFG_SITE_URL

    Running ``fab int sometask`` would print first the integration 
    ``CFG_SITE_URL``, then the production ``CFG_SITE_URL``.
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


def env_defaults(env, name='invenio', prefix=None, python=None, **kwargs):
    """
    Setup defaults in environment.

    The method will by default try to guess
    
    :param name:
    :param prefix:
    :param python:

    .. note:
    
       This can be overridden by the user, though it is not recommended.
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

    if python is None:
        pythonbin = 'python'
    else:
        python_versions = pythonbrew_versions()
        if python in python_versions:
            pythonbin = python_versions[python]
        else:
            python_versions = python_versions.keys()
            python_versions.sort()
            abort("Unknown Python version %s. Available versions are %s" % (
                  python, ", ".join(python_versions)))

    env.update({
        'WITH_VIRTUALENV': True,
        'WITH_DEVSERVER': True,
        'WITH_WORKDIR': True,
        'WITH_DEVSCRIPTS': True,
        'PYTHON': pythonbin,
        'ACTIVATE': '. %(CFG_INVENIO_PREFIX)s/bin/activate',
        'CFG_INVENIO_REPOS': [],
        'CFG_INVENIO_CONF': 'etc/invenio-local.conf',
        'CFG_INVENIO_PREFIX': prefix,
        'CFG_INVENIO_SRCDIR' : os.path.join(prefix, 'src/invenio'),
        'CFG_SRCDIR' : os.environ.get('CFG_SRCDIR', os.path.join(prefix, 'src')),
        # Only use CFG_SRCWORKDIR if WITH_WORKDIR is True
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

        # FIXME: Should be removed, so Inspire stuff is not integrated in main
        # source file.
        'CFG_INSPIRE_SITE' : False,
    })

    env.CFG_INVENIO_REPOS = [
        ('invenio', {
            'repository' : 'http://invenio-software.org/repo/invenio/',
            'ref': 'master',
            'bootstrap_targets': ['all', 'install', 'install-mathjax-plugin', 'install-ckeditor-plugin', 'install-pdfa-helper-files', 'install-jquery-plugins', ],
            'deploy_targets': ['all', 'check-upgrade', 'install', ],
            'requirements': ['requirements.txt', 'requirements-extra.txt', ],
            #'configure_hook': None, # Can be specified if you want to override default behaviour (./configure --with-prefix=.. --with-python=..)
            #'prepare_hook': None, # Can be specified if you want to override default behaviour  (aclocal && autoconf && automake)
        }),
    ]

    return env


def env_override(env, this_repo, this_ref, override={}, global_overrides=None ):
    """ Override default values for repository """
    if global_overrides:
        try:
            this_repo_dict = global_overrides[this_repo][this_ref]
        except KeyError:
            return env
    elif override:
        this_repo_dict = override
    else:
        try:
            this_repo_dict = GLOBAL_REFS_OVERRIDE[this_repo][this_ref]
        except KeyError:
            return env

    def _mapper(x):
        repo, repo_dict = x

        if repo == this_repo:
            repo_dict.update(this_repo_dict)
            if this_ref:
                repo_dict['ref'] = this_ref
        return (repo, repo_dict)

    env.CFG_INVENIO_REPOS = map(_mapper, env.CFG_INVENIO_REPOS)

    return env


def env_make_name(prefix, python, ref):
    """ Generate a MySQL friendly environment name. """
    ref = ref.split("/")
    ref = ref[-1].replace("-","_")
    python = python.replace(".","")
    
    prefix = prefix.replace("_","").replace("-","")

    name = "%s%s%s" % (prefix, python, ref)
    if len(name) > 16:
        name = name.replace("_", "", len(name) - 16)
        return name[:16]

    return name
