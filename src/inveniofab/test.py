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
Tasks for creating and loading a test fixture package to easily run tests
against a known state.
"""

from fabric.api import task, puts, env, roles
from fabric.colors import cyan
from fabric.contrib.console import confirm
from inveniofab.mysql import mysql_dump, mysql_load
from inveniofab.git import repo_all_configure_make
from inveniofab.utils import sudo_local
import os


@task
@roles('web')
def test_clean():
    """ Clean Invenio logs and temporary files """
    puts(cyan(">>> Cleaning Invenio installation..." % env))
    sudo_local("rm -Rf %(CFG_INVENIO_PREFIX)s/var/tmp/ooffice-tmp-files/*" % env)
    sudo_local("rm -Rf %(CFG_INVENIO_PREFIX)s/var/tmp-shared/*" % env, user=env.CFG_INVENIO_USER)
    sudo_local("rm -Rf %(CFG_INVENIO_PREFIX)s/var/tmp/*" % env, user=env.CFG_INVENIO_USER)
    sudo_local("rm -Rf %(CFG_INVENIO_PREFIX)s/var/log/*" % env, user=env.CFG_INVENIO_USER)
    sudo_local("rm -Rf %(CFG_INVENIO_PREFIX)s/var/cache/*" % env, user=env.CFG_INVENIO_USER)
    sudo_local("""echo "TRUNCATE schTASK;" | %(CFG_INVENIO_PREFIX)s/bin/dbexec""" % env, user=env.CFG_INVENIO_USER)
    sudo_local("""echo "TRUNCATE session;" | %(CFG_INVENIO_PREFIX)s/bin/dbexec""" % env, user=env.CFG_INVENIO_USER)


@task
@roles('web')
def test_dump():
    """ Dump a test environment """
    test_reset_admin()
    test_clean()

    puts(cyan(">>> Creating test package..." % env))

    sudo_local("rm -Rf %(CFG_INVENIO_PREFIX)s/tests/" % env, user=env.CFG_INVENIO_USER)
    sudo_local("mkdir -p %(CFG_INVENIO_PREFIX)s/tests/var/" % env, user=env.CFG_INVENIO_USER)
    sudo_local("mkdir -p %(CFG_INVENIO_PREFIX)s/tests/etc/" % env, user=env.CFG_INVENIO_USER)
    sudo_local("sudo rsync --delete -rLptgoDv %(CFG_INVENIO_PREFIX)s/var/ %(CFG_INVENIO_PREFIX)s/tests/var/" % env)
    sudo_local("sudo rsync --delete -rLptgoDv %(CFG_INVENIO_PREFIX)s/etc/ %(CFG_INVENIO_PREFIX)s/tests/etc/" % env)

    mysql_dump(outputdir=os.path.join(env.CFG_INVENIO_PREFIX, "tests"))


@task
@roles('web')
def test_reset_admin():
    """ Reset admin password """
    puts(cyan(">>> Resetting Invenio admin password..." % env))
    sudo_local("""echo "UPDATE user SET password=AES_ENCRYPT(email,'') WHERE nickname='admin';" | %(CFG_INVENIO_PREFIX)s/bin/dbexec""" % env, user=env.CFG_INVENIO_USER)


@task
@roles('web')
def test_load(repo=None, quite=True):
    """ Load test environment """
    if quite or confirm(cyan("Run step load_files?")):
        puts(cyan(">>> Loading test package..." % env))
        sudo_local("rsync --delete -rLptgoDv %(CFG_INVENIO_PREFIX)s/tests/var/ %(CFG_INVENIO_PREFIX)s/var/" % env)
        sudo_local("rsync --delete -rLptgoDv %(CFG_INVENIO_PREFIX)s/tests/etc/ %(CFG_INVENIO_PREFIX)s/etc/" % env)

    if quite or confirm(cyan("Run step load_db?")):
        mysql_load(dumpfile=os.path.join(env.CFG_INVENIO_PREFIX, "tests/%s.sql.gz" % env.CFG_DATABASE_NAME))

    if quite or confirm(cyan("Run step configure_make_install?")):
        repo_all_configure_make(repo, target_key='deploy_targets')
