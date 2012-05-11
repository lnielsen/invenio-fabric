# -*- coding: utf-8 -*-
#
# A Fabric file for installing, deploying and running Invenio on CERN 
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
Fabric tasks for bootstrapping, installing and deploying Invenio demo site on 
CERN Scientific Linux 5/6 hosts.

The tasks follow the guidelines on installing Invenio on SLC5:

  * http://invenio-software.org/wiki/Installation/InvenioOnSLC5

Example usage:

  fab -u <user> env_atlantis:<host> bootstrap
  fab -u <user> env_atlantis:<host> install
  fab -u <user> env_atlantis:<host> deploy
  fab -u <user> env_atlantis:<host> clean
"""

from fabric.api import task
from inveniofab.api import *
from inveniofab.env import env_init, env_activate

@task
def env_atlantis(host):
    """
    Defines OpenAIRE production environment
    """
    # Initialize environment namespace
    roledefs, envsettings = env_init('env_atlantis')
    
    # Update the role definitions
    roledefs.update({
        'web' : [host, ],
        'db' : [host, ],
        'backend' : [host, ],
    })
    
    # Update environment settings - see inveniofab.env.env_init for all
    # available settings.
    envsettings['invenio']['conffile'] = 'atlantis.conf'
    envsettings['system']['crontab'] = 'crontab'
    
    env_activate('env_atlantis')