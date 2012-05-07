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
Library tasks for configuring and running bibsched.
"""

from fabric.api import sudo, env, roles, task, hide, settings
from inveniofab.env import env_settings

@roles('backend')
@task
def bibsched_start():
    """
    Start bibsched
    """
    sudo("/opt/invenio/bin/bibsched start", user="apache")

    
@roles('backend')
@task
def bibsched_stop():
    """
    Stop bibsched
    """
    sudo("/opt/invenio/bin/bibsched stop", user="apache")

    
@roles('backend')
@task
def bibsched_halt():
    """
    Halt bibsched
    """
    with settings(warn_only = True):
        sudo("/opt/invenio/bin/bibsched halt", user="apache")

    
@roles('backend')
@task
def bibsched_status():
    """
    Bibsched status
    """
    sudo("/opt/invenio/bin/bibsched status", user="apache")

    
@roles('backend')
@task
def bibsched_schedule():
    """
    Schedule bibsched tasks to run
    """
    try:
        tasks = env_settings('bibsched')['schedule']
    except KeyError:
        tasks = []
        
    with settings(warn_only = True):
        for t in tasks:
            sudo("/opt/invenio/bin/%s" % t, user="apache")


@roles('backend')
@task
def bibsched_clear_schedule():
    """
    Clear all bibsched schedule tasks
    """
    if is_running():
        bibsched_halt()
       
    sudo("echo \"DELETE FROM schTASK;\" | sudo -u apache /opt/invenio/bin/dbexec")
        
    
def is_running():
    """
    Determine if bibsched is running
    """
    with settings(hide('warnings', 'running', 'stdout', 'stderr'), warn_only = True):
        output = sudo("/opt/invenio/bin/bibsched status", user="apache")
    
    return "BibSched queue running mode: AUTOMATIC" in output