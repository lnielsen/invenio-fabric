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
Tasks for RabbitMQ management.
"""

from __future__ import with_statement
from fabric.api import roles, sudo, task, env, puts, abort, warn, settings
from fabric.colors import cyan, red
from inveniofab.utils import write_template, sudo_local, exists_local, \
    is_local, python_version


@task
def rabbitmq_conf():
    pass


@task
@roles('web')
def rabbitmq_add_user(user, password):
    """
    Add a RabbitMQ user
    """
    rabbitmqctl("add_user", user, password)


@task
@roles('web')
def rabbitmq_add_vhost(name):
    """
    Add a RabbitMQ vhost
    """
    rabbitmqctl("add_vhost", name)


@task
@roles('web')
def rabbitmq_set_user_permissions(vhost, user, tags=['management']):
    """
    Set permission for user to access vhost and allow WebUI login
    """
    rabbitmqctl("set_permissions", "-p", vhost, user, '".*"', '".*"', '".*"')
    for t in tags:
        rabbitmqctl("set_user_tags", user, t)


def rabbitmqctl(*commands):
    sudo_local("rabbitmqctl %s" % " ".join(commands))
