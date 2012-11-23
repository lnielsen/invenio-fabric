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
Compound tasks to perform bigger operations like bootstrapping Invenio.
"""

from fabric.api import task, env
from fabric.colors import cyan
from fabric.contrib.console import confirm
from inveniofab.devserver import devserver_conf
from inveniofab.git import repo_update, repo_install
from inveniofab.invenio import invenio_conf, invenio_createdb, \
    invenio_upgrade
from inveniofab.mysql import mysql_createdb, mysql_dump, mysql_load, \
    mysql_dropdb
from inveniofab.venv import venv_create, venv_requirements, venv_dump, \
    venv_load, venv_drop
# FIXME: See note in bootstrap() method regarding inspire_dbchanges
from inveniofab.inspire import inspire_dbchanges


@task
def bootstrap(with_db=True, quite=False, **kwargs):
    """
    Bootstrap an Invenio installation
    
    Bootstrap will run the following tasks:
    
     * ``mysql_dropdb`` - to drop an existing database if it exists.
     * ``mysql_createdb`` - to create database and user.
     * ``venv_create`` - to create a virtual environment.
     * ``repo_update`` - to checkout source code from repositories.
     * ``venv_requirements`` - to install Python requirements.
     * ``repo_install`` - to install all repositories.
     * ``invenio_conf`` - to configure Invenio.
     * ``devserver_conf`` - to configure the development server.
     * ``invenio_createdb`` - to create Invenio database tables.

    If a task fails, you can re-run bootstrap and skip the initial steps which
    already was completed.

    :param quite: Default ``False``. Set to ``True`` to disable user confirmation.
    :param with_db: Default ``True``. Run database related tasks to create the database.
    """

    def _confirm_step(func, *args, **kwargs):
        if quite or confirm(cyan("Run step %s?" % func.__name__)):
            func(*args, **kwargs)

    if with_db:
        _confirm_step(mysql_dropdb)
        _confirm_step(mysql_createdb)
    _confirm_step(venv_create)
    _confirm_step(repo_update, **kwargs)
    _confirm_step(venv_requirements)
    _confirm_step(repo_install, targets_key='bootstrap_targets')
    _confirm_step(invenio_conf)
    if env.WITH_DEVSERVER:
        _confirm_step(devserver_conf)
    if with_db:
        _confirm_step(invenio_createdb)
    # FIXME: Generalize below to have hooks in the bootstrap process, which can be
    # customized for each individual overlay (e.g. OpenAIRE/INSPIRE needs to create
    # extra tables etc., load demo records?)
    if env.CFG_INSPIRE_SITE:
        _confirm_step(inspire_dbchanges)


@task
def install(quite=False, **kwargs):
    """
    Install repositories
    
    The task will checkout latest changes for the repositories, run make install,
    ``inveniocfg --update-all --upgrade``.
    
    :param quite: Default ``False``. Set to ``True`` to disable user confirmation.
    """

    def _confirm_step(func, *args, **kwargs):
        if quite or confirm("Run step %s?" % func.__name__):
            func(*args, **kwargs)

    _confirm_step(repo_update, **kwargs)
    _confirm_step(repo_install, targets_key='deploy_targets')
    _confirm_step(invenio_conf)
    _confirm_step(invenio_upgrade)


@task
def dump():
    """
    Archive installation
    
    Dump a database and virtual environment to an archive which can later be
    restored with :meth:`~load`.
    """
    mysql_dump()
    venv_dump()


@task
def load():
    """
    Load archived installation
    
    Load an archived virtual environment and database which was dumped with
    :meth:`~dump`.
    """
    venv_load()
    mysql_load()


@task
def drop():
    """
    Remove installation
    
    Remove virtual environment, database and database user.
    """
    venv_drop()
    mysql_dropdb()
