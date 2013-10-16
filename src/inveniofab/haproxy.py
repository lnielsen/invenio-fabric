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
@roles('lb')
def haproxy_conf():
    """ Upload HAProxy conf """
    puts(cyan(">>> Creating and configuring celery init.d script..." % env))

    local = 'haproxy.cfg'
    remote = '/etc/haproxy/haproxy.cfg'

    puts(">>> Writing haproxy.cfg to %s ..." % remote)
    try:
        write_template(remote, env, tpl_file=local, use_sudo=True)
    except TemplateNotFound:
        puts(red("Could not find template %s" % local))


@task
@roles('lb')
def haproxy_disable_server(servername):
    haproxy_server_action(servername, action='disable')

@task
@roles('lb')
def haproxy_enable_server(servername):
    haproxy_server_action(servername, action='enable')


def haproxy_server_action(servername, action='disable'):
    from fabric.api import env
    backends = env.get('HAPROXY_BACKENDS', None)
    if not backends:
        puts(red(">>> HAPROXY_BACKENDS configuration variable not defined ..."))
        return

    if servername not in backends:
        puts(red(">>> No HAProxy backends found for server %s (did you configure HAPROXY_BACKENDS)..." % servername))

    servers = backends[servername]

    if action == 'disable':
        puts(cyan(">>> Disabling %s ..." % ", ".join(servers)))
    else:
        puts(cyan(">>> Enabling %s ..." % ", ".join(servers)))

    cmd = ";".join(["""echo "%s server %s" | socat stdio /var/lib/haproxy/stats""" % (action, x) for x in servers])
    sudo(cmd)

@task
@roles('lb')
def haproxy_start():
    """ Start Celery """
    sudo_local("/etc/init.d/haproxy start" % env)


@task
@roles('lb')
def haproxy_restart():
    """
    Restart Celery
    """
    sudo_local("/etc/init.d/haproxy restart" % env)


@task
@roles('lb')
def haproxy_stop():
    """ Stop Celery """
    sudo_local("/etc/init.d/haproxy stop" % env)
