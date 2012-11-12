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
Definition of Invenio Fabric API. To make all the library tasks available
in a fabfile.py you just have to have the following import in the top
of your file::

  from inveniofab.api import *
"""

from inveniofab.apache import apache_start, apache_restart, apache_stop
from inveniofab.env import env_defaults, env_get, env_create, env_override, \
    env_make_name
from inveniofab.git import repo_update, repo_setup, repo_prepare, \
    repo_install, repo_make, repo_configure, repo_check
from inveniofab.invenio import invenio_conf, invenio_create_demosite, \
    invenio_createdb, invenio_upgrade
from inveniofab.mysql import mysql_dropdb, mysql_createdb, mysql_load, \
    mysql_dump, mysql_copy
from inveniofab.test import test_load, test_dump, test_clean, test_reset_admin
from inveniofab.venv import venv_create, venv_dump, venv_load, venv_drop, \
    venv_requirements, venv_pyuno_install
from inveniofab.compound import bootstrap, install, dump, load, drop
from inveniofab.devserver import devserver_conf, devserver_install_flask