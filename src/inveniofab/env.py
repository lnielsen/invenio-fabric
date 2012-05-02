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
Configurable compound tasks for bootstrapping, installing, configuring, 
deploying and running Invenio. 
"""

from fabric.api import env, execute, abort, task

# ==============
# Compound tasks
# ==============
@task
def install():
    """
    Install Invenio and configure installation from scratch
    """
    _run_task_group('install')

@task
def clean():
    """
    Clean existing Invenio installation
    """
    _run_task_group('clean')

@task
def deploy():
    """
    Deploy Invenio from latest master 
    """
    _run_task_group('deploy')

@task
def bootstrap():
    """
    Bootstrap host system(s) 
    """
    _run_task_group('bootstrap')


def _run_task_group(arg):
    """
    Helper function to run a task group
    """
    try:
        import inveniofab.api
        
        for task in env_settings('tasks')[arg]:
            if not callable(task):
                task = getattr(inveniofab.api, task)
            execute(task)
    except AttributeError:
        abort("No %s tasks defined." % arg)

# =======================
# Default Fabric settings
# =======================
def env_init(name):
    """
    Initialize default environment
    
    ENV_SETTINGS is a dictionary of settings that is initialized by
    an environment. The settings are used to configure the tasks
    for each specific environment (e.g. which conf file to use,
    database name, bibsched tasks etc). Following is a short reference
    of settings:
    
      * localconf: Local path to an invenio-local.conf for env.
      * crontab: Local path to a crontab file for env.
      * schedule: A list of string commands used to set the 
      * db:
      * dbdump_dir:    
    """
    if not hasattr(env, 'ENVIRONMENTS'):
        env.ENVIRONMENTS = {
            'defs' : {},
            'default' : None,
            'active' : None,
        }

    if name not in env.ENVIRONMENTS:
        env_setdefault(name)
        env.ENVIRONMENTS['defs'][name] = {
            'roledefs' : {
                'web' : [],
                'db' : [],
                'backend' : [],
            },
            'settings' : {
                'tasks' : {
                    'bootstrap' : ['python_prepare', 'selinux_prepare', 'mysql_prepare', 'mysql_createdb', 'apache_prepare', 'apache_configure'],
                    'install' : ['invenio_install', 'invenio_configure', 'libreoffice_prepare', 'apache_restart'],
                    'deploy' : ['invenio_deploy', 'apache_restart'],
                    'clean' : ['python_clean', 'apache_clean', 'apache_restart', 'mysql_dropdb', 'invenio_clean',],
                },
                'bibsched' : {
                    'schedule' : [
                        "bibindex -f50000 -s5m -u admin",
                        "bibrank -f50000 -s5m -u admin",
                        "bibreformat -oHB -s5m -u admin",
                        "webcoll -v0 -s5m -u admin",
                        "bibsort -s5m -u admin",
                        "bibrank -f50000 -R -wwrd -s14d -LSunday -u admin",
                        "bibsort -R -s7d -L 'Sunday 01:00-05:00' -u admin",
                        "inveniogc -a -s7d -L 'Sunday 01:00-05:00' -u admin",
                        "batchuploader --documents -s20m -u admin",
                        "batchuploader --metadata -s20m -u admin",
                        "dbdump -s 20h -L '22:00-06:00' -n 10 -u admin",
                        "oairepositoryupdater -s1h -u admin",
                        "oaiharvest -s 24h  -u admin",
                    ]
                },
                'invenio' : {
                    'conffile' : [],
                },
                'mysql' : {
                    'db' : { 'name' : 'invenio', },
                    'dbdump_dir' : None,
                },
                'system' : {
                    'crontab' : None,
                },
            },
        }
    env_setdefault(name)
    return (env.ENVIRONMENTS['defs'][name]['roledefs'], env.ENVIRONMENTS['defs'][name]['settings']) 
        

def env_setdefault(name):
    """
    Set an initialized environment as default (used when editing the settings)
    """
    if not hasattr(env, 'ENVIRONMENTS'):
        abort("You must first initialize an environment before calling env_setdefault.")
    env.ENVIRONMENTS['default'] = name
    

def env_default():
    """
    Get the current default environment (used when editing the settings).
    """
    try:
        return env.ENVIRONMENTS['defs'][env.ENVIRONMENTS['default']]
    except AttributeError:
        abort("You must first initialize an environment before calling env_getdefault.")
    except KeyError:
        abort("No default environment set.")
    

def env_activate(name):
    """
    Activate an environment (so env_settings will return values from this env).
    """
    env.roledefs = env.ENVIRONMENTS['defs'][name]['roledefs']
    env.ENV_SETTINGS = env.ENVIRONMENTS['defs'][name]['settings']

    
def env_settings(module, envname = None):
    """
    Get settings for a particular module.
    """
    return env.ENV_SETTINGS[module] if not envname else env.ENVIRONMENTS['defs'][envname]['settings'][module]

