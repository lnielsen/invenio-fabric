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

import os
from fabric.api import puts, env, task, abort, roles
from fabric.colors import red, cyan
from fabric.contrib.console import confirm
from inveniofab.utils import write_template, sudo_local
from jinja2.exceptions import TemplateNotFound


@task
@roles('workers')
def celery_initd():
    """ Upload and update celeryd init script """
    puts(cyan(">>> Creating and configuring celery init.d script..." % env))

    local = 'celeryd'
    remote = '/etc/init.d/celeryd'

    puts(">>> Writing celeryd to %s ..." % remote)
    try:
        write_template(remote, env, tpl_file=local, use_sudo=True)
    except TemplateNotFound:
        puts(red("Could not find template %s" % local))

    sudo_local("chmod a+x %s" % remote)


@task
@roles('workers')
def celery_start():
    """ Start Celery """
    sudo_local("/etc/init.d/celeryd start" % env)


@task
@roles('workers')
def celery_restart():
    """
    Restart Celery
    """
    sudo_local("/etc/init.d/celeryd restart" % env)


@task
@roles('workers')
def celery_stop():
    """ Stop Celery """
    sudo_local("/etc/init.d/celeryd stop" % env)
