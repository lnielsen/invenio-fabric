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
Compound tasks to perform bigger operations like bootstrapping Invenio
"""

from fabric.api import task, env
from inveniofab.devserver import devserver_conf
from inveniofab.git import repo_update, repo_install
from inveniofab.invenio import invenio_conf, invenio_createdb, \
    invenio_upgrade
from inveniofab.mysql import mysql_createdb, mysql_dump, mysql_load, \
    mysql_dropdb
from inveniofab.venv import venv_create, venv_requirements, venv_dump, \
    venv_load, venv_drop


@task
def bootstrap(with_db=True, **kwargs):
    """ Bootstrap Invenio installation """
    if with_db:
        mysql_createdb()
    venv_create()
    repo_update(**kwargs)
    venv_requirements()
    repo_install(targets_key='bootstrap_targets')
    invenio_conf()
    if env.WITH_DEVSERVER:
        devserver_conf()
    if with_db:
        invenio_createdb()


@task
def install(**kwargs):
    """ Install changes """
    repo_update(**kwargs)
    repo_install(targets_key='deploy_targets')
    invenio_conf()
    invenio_upgrade()


@task
def dump():
    """ Archive installation """
    mysql_dump()
    venv_dump()


@task
def load():
    """ Load archived installation """
    venv_load()
    mysql_load()


@task
def drop():
    """ Remove installation """
    venv_drop()
    mysql_dropdb()
