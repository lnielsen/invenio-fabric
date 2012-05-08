# -*- coding: utf-8 -*-
#
# A Fabric file for ioverlaynstalling, deploying and running Invenio on CERN 
# hosts running SLC5.
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
Example of a more complex usage of invenio-fabric. For instance you
want to install an extra overlay on top of Invenio.

Example usage::

   fab -u <user> env_overlay_dev install
   fab -u <user> env_overlay_dev deploy
   fab -u <user> env_overlay_dev copy:env_overlay_prod
   
Most tasks can be executed standlone via:   
   
   fab -u <user> env_overlay_prod <task name>
   
Run ``fab -l`` to see list of possible tasks.

"""

from fabric.api import roles, cd, run, sudo, run, task
from fabric.contrib.files import exists
from inveniofab.api import *
from inveniofab.env import env_init, env_setactive, env_settings

# ======================
# Extra task for 
# ======================
@roles('web')
@task
def overlay_install():
    """
    Install overlay
    """
    if not exists("/tmp/overlay-invenio"):
        with cd("/tmp"):
            run("git clone http://.../overlay-invenio.git") 

    with cd("/tmp/overlay-invenio"):
        run("make")
        sudo("make install", user = "apache")


@roles('web')
@task
def overlay_deploy():
    """
    Deploy overlay 
    """
    with cd("/tmp/overlay-invenio"):
        run("git pull")
        run("make -s")
        sudo("make install", user = "apache")
        sudo("/opt/invenio/bin/inveniocfg --update-all", user = "apache")


@roles('web')
@task
def overlay_clean():
    """
    Clean overlay
    """
    with cd("/tmp"):
        run("rm -Rf overlay-invenio")
        
        
@roles('web')
@task
def overlay_upgrade():
    """
    Upgrade current production deployment to latest master.
    """
    # Create missing tables
    sudo("/opt/invenio/bin/dbexec < /opt/invenio/lib/sql/invenio/tabcreate.sql", user = "apache")

    # Apply table updates
    sudo("echo \"ALTER TABLE schTASK ADD sequenceid int(8) NULL default NULL;\" | sudo -u apache /opt/invenio/bin/dbexec")
    # .....
    
    # Ensure latest overlay tables are installed 
    overlay_install()

    # Add logical field: DOI    
    sudo("echo \"INSERT INTO field (name,code) VALUES ('DOI','doi');\" | sudo -u apache /opt/invenio/bin/dbexec")
    sudo("echo \"INSERT INTO tag (name,value) VALUES ('doi','0247_a');\" | sudo -u apache /opt/invenio/bin/dbexec")
    # ...
    
    invenio_updateconf()

   
@roles('web')
@task
def overlay_copy( from_env=None ):
    """
    Copy overlay production environment. 
    """
    if not from_env:
        from_env = env_settings('copy')['from_env']
    
    mysql_copy(from_env)
    copy_files()


@roles('web')
@task
def overlay_datamigration( from_env=None ):
    """
    Data migration for copied environment.
    """
    invenio_reset_adminpw()
    bibsched_clear_schedule()
    invenio_fix_filelinks('overlay.cern.ch')

# =======================
# Environment definitions
# =======================
@task
def env_overlay_prod():
    """
    Defines overlay production environment
    """
    roledefs, envsettings = env_init(env_overlay_prod.__name__)
    
    roledefs.update({
        'web' : ['overlay.cern.ch', ],
        'db' : ['overlay.cern.ch', ],
        'backend' : ['overlay.cern.ch', ],
    })
    
    envsettings['invenio']['conffile'] = 'overlay-prod.conf'
    envsettings['mysql']['dbdump_dir'] = '/afs/cern.ch/project/cds/overlay/'
    envsettings['bibsched']['schedule'] = [
        "bibindex -f50000 -s5m -u admin",
        "bibrank -f50000 -s5m -u admin",
        "bibreformat -s5m -u admin",
        "webcoll -s5m -u admin",
        "dbdump  -o %s -L 22:00-03:00 -n 10 -u admin -s1d" % envsettings['mysql']['dbdump_dir'],
        "oairepositoryupdater -s1h -u admin",
        "oaiharvest -s 24h -u admin",
    ], 
    _common(envsettings)
    env_setactive(env_overlay_prod.__name__)


@task
def env_overlay_dev():
    """
    Defines overlay integration environment
    """
    roledefs, envsettings = env_init(env_overlay_dev.__name__)
    roledefs.update({
        'web' : ['overlay-dev.cern.ch', ],
        'db' : ['overlay-dev.cern.ch', ],
        'backend' : ['overlay-dev.cern.ch', ],
    })
    envsettings['invenio']['conffile'] = 'overlay-dev.conf'
    envsettings['mysql']['dbdump_dir'] = '/tmp/mysql_backups/'

    # Settings related to copying of an environment.    
    envsettings['tasks']['copy'] = ['bibsched_halt', overlay_copy, overlay_upgrade, overlay_datamigration, 'bibsched_start', 'bibsched_schedule', ]
    envsettings['system']['copy'] = {
        'owner' : 'apache:apache',
        'local' : '/opt/invenio/',
        'remote' : 'overlay.cern.ch:/opt/invenio/',
        'files' : [
            "etc/bibclassify/eurovoc-en.txt",
            # ...
        ],
        'dirs' : [
            "var/data/",
        ],                                  
    }
    envsettings['bibsched']['schedule'] += [
        "bibtasklet -T bst_some_task -u admin -s1d",
    ]
    _common(envsettings)
    env_setactive(env_overlay_dev.__name__)


def _common(envsettings):
    """
    Common development and production settings
    """
    # Issues with 'libreoffice_prepare'
    envsettings['tasks']['install'] = ['mysql_createdb', 'apache_configure', 'invenio_install', 'invenio_configure', 'overlay_install', 'apache_restart', 'crontab_install']
    envsettings['tasks']['deploy'] = ['invenio_deploy', 'overlay_deploy', 'apache_restart']
    envsettings['tasks']['clean'] += ['overlay_clean']
    envsettings['system']['crontab'] = 'crontab'
    envsettings['mysql']['db']['name'] = 'overlay'