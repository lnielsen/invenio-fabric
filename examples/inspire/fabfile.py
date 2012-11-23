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
Fabric tasks for bootstrapping, installing, deploying and running INSPIRE.

Examples
--------
Bootstrap INSPIRE with Python 2.6
  fab loc:py=26 bootstrap

Configure OpenAIRE repository to use with environment
  fab loc:py=26,ref=master repo_configure:inspire
"""

from fabric.api import task, puts, local
from fabric.colors import cyan
from inveniofab.api import *
from inveniofab.utils import template_hook_factory
import os


@task
def loc(activate=True, py=None, ref=None, invenio='master', **kwargs):
    """
    Local environment (example: loc:py=24,ref=master)
    """
    env = env_create('loc', name=env_make_name('inspireprod', py or '', ref or ''),
                     activate=activate, python=py, **kwargs)

    # Do not use git-new-workdir
    env.WITH_WORKDIR = False
    env.CFG_SRCWORKDIR = env.CFG_SRCDIR

    # FIXME: Should probably be generalized via hooks in the bootstrap task instead.
    # Adds specific inspire steps to, e.g bootstrap task
    env.CFG_INSPIRE_SITE = 1

    # Setup Invenio/INSPIRE source directories (works just as short-cuts)
    # Their path must match CFG_SRCDIR/<reponame> where <reponame> is defined
    # in CFG_INVENIO_REPOS.
    env.CFG_INVENIO_SRCDIR = os.path.join(env.CFG_SRCDIR, 'invenio-inspire-ops')
    env.CFG_INSPIRE_SRCDIR = os.path.join(env.CFG_SRCDIR, 'inspire')

    env.CFG_INVENIO_REPOS = [
        ('invenio-inspire-ops', {
            'repository': 'ssh://%(user)s@lxplus.cern.ch/afs/cern.ch/project/inspire/repo/invenio-inspire-ops.git' % env,
            'ref': 'prod',
            'bootstrap_targets': ['all', 'install', 'install-mathjax-plugin', 'install-ckeditor-plugin', 'install-pdfa-helper-files', 'install-jquery-plugins', ],
            'deploy_targets': ['all', 'install', ],
            'requirements': ['requirements.txt', 'requirements-extra.txt']
        }),
        ('inspire', {
            'repository': 'ssh://%(user)s@lxplus.cern.ch/afs/cern.ch/user/s/simko/public/repo/inspire.git' % env,
            'ref': 'master',
            'bootstrap_targets': ['install', ],
            'deploy_targets': ['install', ],
            'configure_hook': template_hook_factory('config-local.mk', '%(topsrcdir)s/config-local.mk'),
            'prepare_hook': None
        }),
    ]

    env.CFG_DATABASE_HOST = 'localhost'
    env.CFG_DATABASE_PORT = 3306
    env.CFG_INVENIO_ADMIN = 'javier.martin.montull@cern.ch'

    # If no database or username is specified a new database with the same
    # name as the virtualenv will be created. Also a user with the env username
    # will be created
    #env.CFG_DATABASE_NAME = 'invenio'
    #env.CFG_DATABASE_USER = 'invenio'

    # Set default Invenio branch
    env = env_override(env, 'invenio', invenio, override={})
    return env

# =======================
# INSPIRE specific tasks
# =======================
@task
def inspire_dbchanges():
    """ Perform INSPIRE db changes """
    from fabric.api import env
    puts(cyan(">>> Updating tables from INSPIRE..." % env))
    ctx = {
        'topsrcdir': repo_check('inspire', check_path=True, workdir=True),
    }
    ctx.update(env)
    local("cd %(topsrcdir)s; make install-dbchanges" % ctx)

    query_output = local('echo "select max(id) from schTASK;" | dbexec', capture=True)
    task_id = query_output.split('\n')[-1]
    puts(cyan(">>> Running webcoll task %s..." % task_id))

    ctx.update({'webcoll_task_id': task_id})
    local("%(CFG_INVENIO_PREFIX)s/bin/webcoll %(webcoll_task_id)s" %
          ctx)
