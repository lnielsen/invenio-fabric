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
from fabric.api import local, puts, env, task, abort, warn
from fabric.colors import red, cyan
from fabric.contrib.console import confirm
from inveniofab.utils import write_template
from jinja2.exceptions import TemplateNotFound

#
# Default configuration template
#

INVENIO_LOCAL_TPL = u"""
[Invenio]
CFG_BIBSCHED_PROCESS_USER = {{CFG_INVENIO_USER}}
CFG_DATABASE_HOST = {{CFG_DATABASE_HOST}}
CFG_DATABASE_PORT = {{CFG_DATABASE_PORT|default(3306)}}
CFG_DATABASE_NAME = {{CFG_DATABASE_NAME}}
CFG_DATABASE_USER = {{CFG_DATABASE_USER}}
CFG_DATABASE_PASS = {{CFG_DATABASE_PASS}}
CFG_SITE_URL = http://{{CFG_INVENIO_HOSTNAME}}:{{CFG_INVENIO_PORT_HTTP}}
# For production environments, change http to https in next line
CFG_SITE_SECURE_URL = http://{{CFG_INVENIO_HOSTNAME}}:{{CFG_INVENIO_PORT_HTTPS}}
CFG_SITE_ADMIN_EMAIL = {{CFG_INVENIO_ADMIN}}
CFG_SITE_SUPPORT_EMAIL = {{CFG_INVENIO_ADMIN}}
CFG_SITE_NAME = Atlantis Fictive Institute of Science
CFG_SITE_NAME_INTL_fr = Atlantis Institut des Sciences Fictives
# Next two is only for runnning a debugging mail server
{% if CFG_MISCUTIL_SMTP_HOST and CFG_MISCUTIL_SMTP_PORT %}
CFG_MISCUTIL_SMTP_HOST = {{CFG_MISCUTIL_SMTP_HOST}}
CFG_MISCUTIL_SMTP_PORT = {{CFG_MISCUTIL_SMTP_PORT}}
{% endif %}
CFG_DEVEL_SITE = 0
CFG_SITE_EMERGENCY_EMAIL_ADDRESSES = {'*': '{{CFG_INVENIO_ADMIN}}'}
CFG_WEBSTYLE_INSPECT_TEMPLATES = 0
CFG_FLASK_CACHE_TYPE = redis
"""


@task
def invenio_conf():
    """ Upload and update Invenio configuration """
    puts(cyan(">>> Configuring Invenio..." % env))

    invenio_local = env.get('CFG_INVENIO_CONF', None)
    invenio_local_remote = os.path.join(env.CFG_INVENIO_PREFIX, 'etc/invenio-local.conf')

    if not invenio_local:
        puts(red(">>> CFG_INVENIO_CONF not specified, using built-in template for invenio-local.conf..."))

    puts(">>> Writing invenio-local.conf to %s ..." % invenio_local_remote)
    if not invenio_local:
        write_template(invenio_local_remote, env, tpl_str=INVENIO_LOCAL_TPL)
    else:
        try:
            write_template(invenio_local_remote, env, tpl_file=invenio_local)
        except TemplateNotFound:
            puts(red("Could not find template %s" % invenio_local))
            if not confirm("Use built-in template for invenio-local.conf?"):
                abort("User aborted")
            else:
                write_template(invenio_local_remote, env, tpl_str=INVENIO_LOCAL_TPL)

    inveniocfg("--update-all")


@task
def invenio_upgrade():
    """ Upgrade Invenio """
    puts(cyan(">>> Upgrading Invenio..." % env))
    inveniocfg("--upgrade")


@task
def invenio_createdb():
    """ Create Invenio tables """
    puts(cyan(">>> Creating Invenio tables..." % env))
    inveniocfg("--create-tables")


@task
def invenio_create_demosite():
    """ Create Invenio demo site"""
    puts(cyan(">>> Creating Invenio demo site..." % env))
    inveniocfg("--create-demo-site --load-demo-records")


#
# Helpers
#
def inveniocfg(options):
    """
    Helper to run inveniocfg
    """
    #cmds = " && ".join([]) % env
    local(("%(CFG_INVENIO_PREFIX)s/bin/inveniocfg " % env) + options)
