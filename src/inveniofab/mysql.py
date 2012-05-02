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
Library tasks for configuring and running MySQL for Invenio.
"""

from fabric.api import roles, sudo, env, prompt, run, abort, task
from fabric.contrib.console import confirm
from fabric.contrib.files import exists
from inveniofab.env import env_settings
from inveniofab.utils import slc_version

@roles('db')
@task
def mysql_prepare():
    """
    Prepare MySQL on SLC5 host
    """
    sudo("/sbin/service mysqld start")
    sudo("/sbin/chkconfig mysqld on")
        
    if confirm("Secure MySQL installation?"):
        sudo("/usr/bin/mysql_secure_installation")
        
    # Create DB dump dir
    dumpdir = env_settings('mysql')['dbdump_dir'] or '/opt/invenio/var/log'
    if dumpdir:
        sudo("mkdir -p %s" % dumpdir, user="apache")
        sudo("chown apache:apache %s" % dumpdir, user="apache")
        sudo("chmod 755 %s" % dumpdir, user="apache")


@roles('db')
@task
def mysql_createdb():
    """
    Create database and user for Invenio
    """
    # Create context
    ctx = env_settings('mysql')['db']
    if 'user' not in ctx:
        ctx['user'] = ctx['name']
    if 'password' not in ctx:
        newpw = prompt('Enter new MySQL Invenio user password (typing will be visible, default is my123p$ss):')
        ctx['password'] = "my123p$ss" if not newpw else newpw

    # Escape quote characters
    ctx['password'] = ctx['password'].replace('"', '\"')
    ctx['password'] = ctx['password'].replace("'", "\'")

    # Run commands
    run('mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS %(name)s DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci"' % ctx)
    run('mysql -u root -p -e "GRANT ALL PRIVILEGES ON %(name)s.* TO %(user)s@localhost IDENTIFIED BY \'%(password)s\';"' % ctx)
    run('mysqladmin -u root -p flush-privileges')


@roles('db')
@task
def mysql_dropdb():
    """
    Create database and user for Invenio
    """
    # Create context
    ctx = env_settings('mysql')['db']
    if 'user' not in ctx:
        ctx['user'] = ctx['name']
    
    # Run commands
    run('mysql -u root -p -e "DROP DATABASE IF EXISTS %(name)s"' % ctx)
    run('mysql -u root -p -e "REVOKE ALL PRIVILEGES ON %(name)s.* FROM %(user)s@localhost"' % ctx)
    run('mysqladmin -u root -p flush-privileges')


@roles('db')
@task
def mysql_loaddump( dumpfile ):
    """
    Load MySQL dump file
    """
    if not exists(dumpfile, use_sudo = True):
        abort("File %s does not exists." % dumpfile)
    
    if confirm("This will erease all data in the existing database. Are you sure you want to load %s?" % dumpfile):
        ctx = env_settings('mysql')['db']
        ctx['dumpfile'] = dumpfile
        run('mysql -u root -p -e "DROP DATABASE IF EXISTS %(name)s"' % ctx)
        run('mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS %(name)s DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci"' % ctx)
        run('mysql -u root -f -p %(name)s < %(dumpfile)s' % ctx)