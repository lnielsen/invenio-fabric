# -*- coding: utf-8 -*-
#
# A Fabric file for installing, deploying and running Invenio on CERN 
# SLC5/6 hosts.
#
# Lars Holm Nielsen <lars.holm.nielsen@cern.ch>
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

from inveniofab.apache import apache_clean, apache_configure, apache_prepare, \
    apache_restart
from inveniofab.bibsched import bibsched_halt, bibsched_schedule, bibsched_start, \
    bibsched_status, bibsched_stop, bibsched_clear_schedule
from inveniofab.env import bootstrap, clean, deploy, install, copy
from inveniofab.invenio import invenio_clean, invenio_configure, invenio_deploy, \
    invenio_install, invenio_updateconf, invenio_reset_adminpw, invenio_fix_filelinks
from inveniofab.mysql import mysql_prepare, mysql_loaddump, mysql_dropdb, \
    mysql_createdb, mysql_copy
from inveniofab.python import python_clean, python_prepare
from inveniofab.system import crontab_install, crontab_show, crontab_uninstall, \
    libreoffice_prepare, selinux_prepare, copy_files
