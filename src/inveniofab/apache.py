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
Library tasks for Apache library tasks
"""

from fabric.api import roles, sudo, task
from fabric.contrib.files import append, comment, uncomment, sed

HTTPD_CONF_EXTRAS = [
"Include /opt/invenio/etc/apache/invenio-apache-vhost.conf",
"Include /opt/invenio/etc/apache/invenio-apache-vhost-ssl.conf",
"TraceEnable off",
"SSLProtocol all -SSLv2",
]

@roles('web')
@task
def apache_prepare():
    """
    Prepare Apache on SLC5/6 host
    """
    sudo("/sbin/service httpd start")
    sudo("/sbin/chkconfig httpd on")


@roles('web')
@task
def apache_configure():
    """
    Configure Apache on SLC5/6 host
    """
    apache_conf = "/etc/httpd/conf/httpd.conf"
    append(apache_conf, HTTPD_CONF_EXTRAS, use_sudo = True)
    comment(apache_conf, '^Alias /error/ .+', use_sudo = True)

  
@roles('web')
@task
def apache_clean():
    """
    Remove all configuration directives added to httpd.conf.
    """ 
    for line in HTTPD_CONF_EXTRAS:
        sed("/etc/httpd/conf/httpd.conf", line, "", use_sudo = True)
    uncomment("/etc/httpd/conf/httpd.conf", 'Alias \/error\/ .+', use_sudo = True)


@roles('web')
@task
def apache_restart():
    """
    Restart Apache
    """
    sudo("/sbin/service httpd restart")