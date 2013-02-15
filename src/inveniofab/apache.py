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
Tasks for Apache start/stop/restarting apache.

All tasks assume ``env.CFG_INVENIO_APACHECTL`` is defined and points to your
Apache control script (e.g. ``/etc/init.d/apache2`` or ``../apachectl``). The
script must support the following commands: start, stop, configtest, graceful.

.. warning::

  These tasks are not working locally like the rest Invenio Fabric library.
"""

from fabric.api import roles, sudo, task, env, puts, abort, warn, settings
from fabric.colors import cyan, red
from fabric.contrib.console import confirm
from fabric.contrib.files import append
from inveniofab.utils import write_template, sudo_local, exists_local, is_local
from jinja2.exceptions import TemplateNotFound
import os


@task
@roles('web')
def apache_start():
    """ Start Apache """
    sudo("%(CFG_INVENIO_APACHECTL)s start" % env)


@task
@roles('web')
def apache_restart():
    """
    Restart Apache

    The task will first test the configuration and afterwards gracefully
    restart Apache.
    """
    sudo("%(CFG_INVENIO_APACHECTL)s configtest" % env)
    sudo("%(CFG_INVENIO_APACHECTL)s graceful" % env)


@task
@roles('web')
def apache_stop():
    """ Stop Apache """
    sudo("%(CFG_INVENIO_APACHECTL)s stop" % env)


@task
@roles('web')
def apache_conf():
    """ Upload and update Apache configuration """
    puts(cyan(">>> Configuring Apache..." % env))

    conf_files = ['etc/apache/invenio-apache-vhost.conf', 'etc/apache/invenio-apache-vhost-ssl.conf']
    conf_files = [(p, os.path.join(env.CFG_INVENIO_PREFIX, p)) for p in conf_files]

    for local_file, remote_file in conf_files:
        puts(">>> Writing %s ..." % remote_file)

        try:
            if not exists_local(os.path.dirname(remote_file)):
                sudo_local("mkdir -p %s" % os.path.dirname(remote_file), user=env.CFG_INVENIO_USER)
            write_template(remote_file, env, tpl_file=local_file, use_sudo=True)
        except TemplateNotFound:
            abort(red("Could not find template %s" % local_file))

    apache_conf = env.get('CFG_APACHE_CONF', '/etc/httpd/conf/httpd.conf')
    if confirm("Include created files in %s?" % apache_conf):
        if exists_local(apache_conf, use_sudo=True):
            lines = ["Include %s" % r for (l, r) in conf_files]
            if is_local():
                with settings(host_string="localhost"):
                    append(apache_conf, lines, use_sudo=True)
            else:
                append(apache_conf, lines, use_sudo=True)
        else:
            warn(red("File %s does not exists" % apache_conf))

    sudo_local("%(CFG_INVENIO_APACHECTL)s configtest" % env)
