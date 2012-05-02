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
Library tasks for setting up Python for Invenio on SLC5/6 host.
"""

from fabric.api import roles, run, sudo, task
from fabric.contrib.files import exists

@roles('web')
@task
def python_prepare():
    """
    Setup Python symlinks
    """
    pyver = run("python -c \"import sys;print '%s.%s' % sys.version_info[:2]\"")
    
    sudo("chgrp apache /opt")
    sudo("chmod g+w /opt")
    sudo("mkdir -p /opt/invenio/lib/python/invenio")
    sudo("chown -R apache /opt/invenio/")
    if not exists('/usr/lib64/python%s/site-packages/invenio' % pyver):
        sudo("ln -s /opt/invenio/lib/python/invenio /usr/lib64/python%s/site-packages/invenio"  % pyver )
    if not exists('/usr/lib/python%s/site-packages/invenio'  % pyver):
        sudo("ln -s /opt/invenio/lib/python/invenio /usr/lib/python%s/site-packages/invenio" % pyver)


@roles('web')
@task
def python_clean():
    """
    Setup Python symlinks
    """
    if exists('/usr/lib64/python2.4/site-packages/invenio'):
        sudo("rm -f /usr/lib64/python2.4/site-packages/invenio")
    if exists('/usr/lib/python2.4/site-packages/invenio'):
        sudo("rm -f /usr/lib/python2.4/site-packages/invenio")