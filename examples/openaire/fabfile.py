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
Fabric tasks for bootstrapping, installing, deploying and running OpenAIRE.

Examples
--------
Bootstrap OpenAIRE with Python 2.4 and copy production data
  fab loc:py=24 bootstrap openaire_fixture_load

Configure OpenAIRE repository to use with environment
  fab loc:py=24,ref=master repo_configure:openaire
"""

from fabric.api import task, abort, puts, local, roles, sudo, cd, execute
from fabric.colors import cyan
from fabric.contrib.console import confirm
from inveniofab.api import *
from inveniofab.utils import template_hook_factory
from jinja2.exceptions import TemplateNotFound
import os


@task
def int(activate=True, **kwargs):
    """ Environment: Integration """
    env = env_create('int', activate=activate, **kwargs)

    env.roledefs = {
        'web': ['devhost', ],
        'lb': [],
        'db-master': ['devhost', ],
        'db-slave': [],
        'workers': ['devhost', ],
    }

    env.CFG_SRCDIR = '/opt/src'
    env.CFG_INVENIO_SRCDIR = os.path.join(env.CFG_SRCDIR, 'invenio')
    env.CFG_INVENIO_PREFIX = '/opt/invenio'
    env.CFG_INVENIO_CONF = 'etc/invenio-local.conf'
    env.CFG_INVENIO_HOSTNAME = "devhost"
    env.CFG_INVENIO_DOMAINNAME = ""
    env.CFG_INVENIO_PORT_HTTP = "80"
    env.CFG_INVENIO_PORT_HTTPS = "443"
    env.CFG_INVENIO_USER = 'apache'
    env.CFG_INVENIO_APACHECTL = '/etc/init.d/httpd'
    env.CFG_INVENIO_ADMIN = 'openaire-admin@cern.ch'

    env.CFG_OPENAIRE_SRCDIR = os.path.join(env.CFG_SRCDIR, 'openaire')
    env.CFG_OPENAIRE_PORTAL_URL = "https://test.openaire.eu"

    env.CFG_INVENIO_REPOS = [
        ('invenio', {
            'repository': 'http://invenio-software.org/repo/invenio/',
            'ref': 'origin/maint-1.1',
            'bootstrap_targets': ['all', 'install', 'install-mathjax-plugin', 'install-ckeditor-plugin', 'install-pdfa-helper-files', 'install-jquery-plugins', ],
            'deploy_targets': ['all', 'install', ],
        }),
        ('openaire', {
            'repository': 'http://invenio-software.org/repo/openaire/',
            'ref': 'origin/maint',
            'bootstrap_targets': ['all', 'install', ],
            'deploy_targets': ['all', 'install', ],
        }),
    ]

    env.CFG_DATABASE_DUMPDIR = env.CFG_INVENIO_PREFIX
    env.CFG_DATABASE_HOST = 'somedbhost'
    env.CFG_DATABASE_PORT = 3306
    env.CFG_DATABASE_NAME = 'somedb'
    env.CFG_DATABASE_USER = 'someuser'
    env.CFG_DATABASE_PASS = 'somepassword'
    env.CFG_DATABASE_DROP_ALLOWED = True


@task
def loc(activate=True, py=None, ref=None, invenio='master', **kwargs):
    """
    Local environment (example: loc:py=24,ref=master)
    """
    env = env_create('loc', name=env_make_name('openaire', py or '', ref or ''),
                     activate=activate, python=py, **kwargs)

    # Do not use git-new-workdir
    env.WITH_WORKDIR = False
    env.CFG_SRCWORKDIR = env.CFG_SRCDIR
    
    # Setup Invenio/OpenAIRE source directories (works just as short-cuts)
    # Their path must match CFG_SRCDIR/<reponame> where <reponame> is defined 
    # in CFG_INVENIO_REPOS.
    env.CFG_INVENIO_SRCDIR = os.path.join(env.CFG_SRCDIR, 'invenio')
    env.CFG_OPENAIRE_SRCDIR = os.path.join(env.CFG_SRCDIR, 'openaire')

    # OPENAIRE related variable, needed in invenio-local.conf
    env.CFG_OPENAIRE_PORTAL_URL = ""

    # Append OpenAIRE repository
    env.CFG_INVENIO_REPOS += [
        ('openaire', {
            'repository': 'http://invenio-software.org/repo/openaire/',
            'ref': ref or 'maint',
            'bootstrap_targets': ['all', 'install', ],
            'deploy_targets': ['all', 'install', ],
            'requirements' : ['%(CFG_OPENAIRE_SRCDIR)s/requirements.txt'],
            #'configure_hook': template_hook_factory('config-local.mk','%(topsrcdir)s/config-local.mk'),
            #'prepare_hook': None, # Don't run any hook on prepare
        }),
    ]

    # Set default Invenio branch
    env = env_override(env, 'invenio', invenio, override={})
    return env

# =======================
# OpenAIRE specific tasks
# =======================
@task
def openaire_createdb():
    """ Create OpenAIRE tables """
    from fabric.api import env
    puts(cyan(">>> Creating OpenAIRE tables..." % env))
    ctx = {
        'topsrcdir': repo_check('openaire', check_path=True, workdir=True),
    }
    ctx.update(env)
    local("cd %(topsrcdir)s; make install-tables" % ctx)


@task
def openaire_fixture_load(quite=False):
    """ Fixture: Copy metadata and data from production """
    from fabric.api import env
    puts(cyan(">>> Loading OpenAIRE fixtures..." % env))

    def _confirm_step(func, *args, **kwargs):
        if quite or confirm(cyan("Run step %s?" % func.__name__)):
            func(*args, **kwargs)

    if quite or confirm(cyan("Run step copy_dump")):
        puts(cyan(">>> Getting latest database dump..." % env))
        local("cp `ls -1t /afs/cern.ch/project/cds/OpenAIRE/*.gz | head -n 1` %(CFG_INVENIO_PREFIX)s/%(CFG_DATABASE_NAME)s.sql.gz" % env)

    _confirm_step(mysql_load)
    _confirm_step(test_clean)

    if quite or confirm(cyan("Run step database_upgrade")):
        puts(cyan(">>> Running database upgrade..." % env))
        local("%(CFG_INVENIO_PREFIX)s/bin/inveniocfg --upgrade --yes-i-know" %
              env)

    # Specific to OpenAIRE
    if quite or confirm(cyan("Run step reset_admin")):
        local("""echo "UPDATE user SET password=AES_ENCRYPT(email,''), nickname='admin' WHERE nickname='lnielsen';" | %(CFG_INVENIO_PREFIX)s/bin/dbexec""" % env)
        test_reset_admin()

    ctx = {
        'files': " ".join([
            "etc/bibclassify/eurovoc-en.txt",
            "etc/bibconvert/config/OpenAIRE.tpl",
            "etc/bibconvert/config/OpenAIREmodify.tpl",
            "etc/bibexport/OpenAIRE-sitemap.cfg",
            "etc/bibrank/combine_method.cfg",
            "etc/bibrank/download_similarity.cfg",
            "etc/bibrank/download_total.cfg",
            "etc/bibrank/download_users.cfg",
            "etc/webaccess/robot_keys.dat",
        ]),
    }
    ctx.update(env)

    if quite or confirm(cyan("Run step copy_files")):
        puts(cyan(">>> Copying data files and fixing record URLs..." % env))
        local("""cd %(CFG_INVENIO_PREFIX)s;ssh openaire.cern.ch "cd /opt/invenio && tar -zvcf - %(files)s" | tar xzf -""" % ctx)
        local("""rsync -e ssh --delete -rLptgoDv root@openaire.cern.ch:/opt/invenio/var/data/ %(CFG_INVENIO_PREFIX)s/var/data/""" % env)

    _confirm_step(openaire_fixture_fix_links)
    _confirm_step(openaire_bibsched_tasks)
    puts(cyan(">>> OpenAIRE fixtures loaded..." % env))


@task
def openaire_fixture_fix_links():
    """ Fixture: Change external to internal links """
    from fabric.api import env

    local("rm -Rf %(CFG_INVENIO_PREFIX)s/fix_8564_output.xml" % env)
    local("""%(CFG_INVENIO_PREFIX)s/bin/python %(CFG_OPENAIRE_SRCDIR)s/miscutil/lib/fix_8564.py > %(CFG_INVENIO_PREFIX)s/fix_8564_output.xml""" % env)
    local("""echo "TRUNCATE schTASK;" | %(CFG_INVENIO_PREFIX)s/bin/dbexec""" %
          env)
    local("""%(CFG_INVENIO_PREFIX)s/bin/bibupload -c %(CFG_INVENIO_PREFIX)s/fix_8564_output.xml""" % env)
    local("""%(CFG_INVENIO_PREFIX)s/bin/bibupload 1""" % env)
    local("rm -Rf %(CFG_INVENIO_PREFIX)s/fix_8564_output.xml" % env)


@task
def openaire_test(quite=False):
    """
    Test OpenAIRE
    """
    from fabric.api import env
    puts(cyan(">>> Preparing OpenAIRE test environment..." % env))

    # Load archived environment and re-install OpenAIRE
    test_load(quite=quite)

    if quite or confirm(cyan("Run step test?")):
        puts(cyan(">>> Running tests..." % env))
        local('%(CFG_INVENIO_PREFIX)s/bin/python %(CFG_OPENAIRE_SRCDIR)s/openaire/lib/openaire_deposit_engine_tests.py' % env)
        local('%(CFG_INVENIO_PREFIX)s/bin/python %(CFG_OPENAIRE_SRCDIR)s/openaire/lib/openaire_deposit_webinterface_tests.py' % env)

    if quite or confirm(cyan("Run step openaire_bibsched_tasks?")):
        openaire_bibsched_tasks()


@task
def openaire_bibsched_tasks():
    from fabric.api import env
    puts(cyan(
        ">>> Running bibindex, bibrank, bibreformat and webcoll..." % env))
    local('echo "TRUNCATE schTASK;" | %(CFG_INVENIO_PREFIX)s/bin/dbexec' % env)
    local('%(CFG_INVENIO_PREFIX)s/bin/bibindex -f50000 -s5m -u admin' % env)
    local('%(CFG_INVENIO_PREFIX)s/bin/bibindex 1' % env)
    local('%(CFG_INVENIO_PREFIX)s/bin/bibrank -f50000 -s5m -u admin' % env)
    local('%(CFG_INVENIO_PREFIX)s/bin/bibrank 2' % env)
    local('%(CFG_INVENIO_PREFIX)s/bin/bibreformat -s5m -u admin' % env)
    local('%(CFG_INVENIO_PREFIX)s/bin/bibreformat 3' % env)
    local('%(CFG_INVENIO_PREFIX)s/bin/webcoll -s5m -u admin' % env)
    local('%(CFG_INVENIO_PREFIX)s/bin/webcoll 4' % env)
    local('%(CFG_INVENIO_PREFIX)s/bin/bibtasklet -T bst_openaire_keywords -u admin -s1d' % env)
    local('%(CFG_INVENIO_PREFIX)s/bin/bibtasklet 5' % env)
    local(
        '%(CFG_INVENIO_PREFIX)s/bin/oairepositoryupdater -s1h -u admin' % env)
    local('%(CFG_INVENIO_PREFIX)s/bin/oairepositoryupdater 6' % env)

# ==========================
# OpenAIRE remote deployment
# ==========================


@roles('web')
@task
def deploy(**repos):
    """ Deployment: Prepare source """
    from fabric.api import env

    for repo, ref  in repos.items():
        repo_check(repo, check_path=False)

    for repo, ref  in repos.items():
        puts(" - %s at %s" % (repo, ref))

    if not confirm(cyan("Deploy above repository?")):
        abort("Deployment aborted.")

    sudo("%(CFG_INVENIO_PREFIX)s/bin/bibsched stop" % env, user=env.CFG_INVENIO_USER)
    execute(deploy_source, **repos)
    execute(deploy_install, **repos)
    sudo("%(CFG_INVENIO_PREFIX)s/bin/bibsched start" % env, user=env.CFG_INVENIO_USER)
    execute(apache_restart)


@roles('web')
@task
def deploy_source(**repos):
    """ Deployment: Prepare source """
    from fabric.api import env

    # Check all repositories first
    for repo, ref  in repos.items():
        repo_check(repo, check_path=False)

    for repo, dummy_info  in env.CFG_INVENIO_REPOS:
        if repo in repos:
            ref = repos[repo]
            with cd(os.path.join(env.CFG_SRCDIR, repo)):
                sudo("git fetch", user=env.CFG_INVENIO_USER)
                sudo("git reset --hard %s" % ref, user=env.CFG_INVENIO_USER)
                sudo("make -s clean", user=env.CFG_INVENIO_USER)
                sudo("make -s", user=env.CFG_INVENIO_USER)


@roles('web')
@task
def deploy_install(**repos):
    """ Deployment: Install source code """
    from fabric.api import env

    for repo in repos.keys():
        repo_check(repo, check_path=False)

    for repo, dummy_info  in env.CFG_INVENIO_REPOS:
        if repo in repos:
            with cd(os.path.join(env.CFG_SRCDIR, repo)):
                sudo("make -s install", user=env.CFG_INVENIO_USER)

    sudo("%(CFG_INVENIO_PREFIX)s/bin/inveniocfg --update-all" % env, user=env.CFG_INVENIO_USER)
    sudo("%(CFG_INVENIO_PREFIX)s/bin/inveniocfg --upgrade" % env, user=env.CFG_INVENIO_USER)
