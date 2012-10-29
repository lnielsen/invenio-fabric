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
Invenio Fabric tasks for Apache
"""

from fabric.api import roles, sudo, task, env

@roles('web')
@task
def apache_start():
    """ Restart Apache """
    sudo("%(CFG_INVENIO_APACHECTL)s start" % env)


@roles('web')
@task
def apache_restart():
    """ Restart Apache """
    sudo("%(CFG_INVENIO_APACHECTL)s configtest" % env)
    sudo("%(CFG_INVENIO_APACHECTL)s graceful" % env)


@roles('web')
@task
def apache_stop():
    """ Restart Apache """
    sudo("%(CFG_INVENIO_APACHECTL)s stop" % env)