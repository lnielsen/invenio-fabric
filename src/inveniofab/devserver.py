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
Task to work with devserver
"""

from fabric.api import task, puts, env, local, warn
from fabric.colors import cyan, red
from inveniofab.utils import write_template, python_version
from jinja2.exceptions import TemplateNotFound
import os
import stat

@task
def devserver_conf():
    """ Upload and update Invenio configuration """
    puts(cyan(">>> Configuring invenio-devserver..." % env))

    pyver = python_version()

    local_file = 'config_local.py.tpl'
    local_remote = os.path.join(env.CFG_INVENIO_PREFIX, 'lib/python%s/site-packages/config_local.py' % pyver)

    puts(">>> Writing config_local.py to %s ..." % local_remote)
    try:
        write_template(local_remote, env, tpl_file=local_file)
    except TemplateNotFound:
        warn(red("Could not find template %s" % local_file))


@task
def devserver_install_flask():
    """ Install a Flask devserver """
    puts(cyan(">>> Configuring Flask devserver..." % env))
    
    local_file = 'rundevserver.py.tpl'
    local_remote = os.path.join(env.CFG_INVENIO_PREFIX, 'bin/rundevserver.py')

    puts(">>> Writing rundevserver.py to %s ..." % local_remote)
    try:
        write_template(local_remote, env, tpl_file=local_file)
        local("chmod a+x %s" % local_remote)
    except TemplateNotFound:
        warn(red("Could not find template %s" % local_file))
