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

from fabric.api import roles, sudo, env, abort, put, settings, task
from fabric.contrib.files import contains, sed
from inveniofab.env import env_settings
from inveniofab.utils import slc_version
import os

"""
Library tasks for configuring SLC5/6 system (crontabs, SELinux, OpenOffice).
"""

# ============================
# SELinux library tasks (SLC5)
# ============================
@roles('web')
@task
def selinux_prepare():
    """
    Setup SELinux on host
    """
    slcver = slc_version()
    if slcver and slcver[0] < 6:
        sudo("/usr/sbin/setenforce Permissive")
        sudo("sed -e 's/^SELINUX=enforcing$/SELINUX=permissive/g' < /etc/selinux/config > ~/selinux_config.new")
        sudo("cp ~/selinux_config.new /etc/selinux/config && rm ~/selinux_config.new")


# =========================
# LibreOffice library tasks
# =========================
@roles('web')
@task
def libreoffice_prepare():
    """
    Setup LibreOffice on host
    """
    # Note, editing /etc/sudoers should be moved to Quattor
    slcver = slc_version()
    if slcver and slcver[0] < 6:
        if not contains("/etc/sudoers", "NOPASSWD: /opt/invenio/bin/inveniounoconv", use_sudo = True):
            sed("/etc/sudoers", "^(apache\s+ALL=.+)$", "\\1, (nobody) NOPASSWD: /opt/invenio/bin/inveniounoconv", use_sudo = True)
    sudo("mkdir -p /opt/invenio/var/tmp/ooffice-tmp-files")
    sudo("chown -R nobody /opt/invenio/var/tmp/ooffice-tmp-files")
    sudo("chmod -R 755 /opt/invenio/var/tmp/ooffice-tmp-files")
    sudo("/opt/invenio/bin/inveniocfg --check-openoffice", user = "apache")

# =====================
# Crontab library tasks
# =====================
@roles('backend')
@task
def crontab_install():
    """
    Install crontab on backend server
    """
    crontab = env_settings('system')['crontab']
    if not crontab:
        abort("No crontab defined for environment.")
    if not os.path.exists(crontab):
        abort("Crontab file %s does not exists." % crontab)
    remote = "/opt/invenio/etc/crontab"
    put(crontab, remote, use_sudo = True)
    sudo("chown apache:apache %s" % remote)
    sudo("chmod 644 %s" % remote)
    sudo("crontab %s" % remote, user = "apache")


@roles('backend')
@task
def crontab_uninstall():
    """
    Uninstall crontab on backend server
    """
    with settings( warn_only=True ):
        sudo("crontab -r", user = "apache")

        
@roles('backend')
@task
def crontab_show():
    """
    Show installed crontab on backend server
    """
    with settings( warn_only=True ):
        sudo("crontab -l", user = "apache")