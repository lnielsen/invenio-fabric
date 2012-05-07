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
from fabric import state

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


@task
def copy(from_env):
    """
    Copy data from one environment to another  
    """
    env_load(from_env)
    env_settings('copy')['from_env'] = from_env 
    _run_task_group('copy')


def _run_task_group(task_name, *args, **kwargs):
    """
    Helper function to run a task group
    """
    try:
        for task in env_settings('tasks')[task_name]:
            if not callable(task):
                task = state.commands[task]
            execute(task, *args, **kwargs)
    except AttributeError:
        abort("No %s tasks defined." % task_name)
    except KeyError:
        abort("Subtask %s not found." % task)


def _copy_not_supported(from_env):
    """
    By default, copying an environment is not supported
    """
    current_env = env_active()
    abort("Copying %s to %s is not supported." % (from_env, current_env))


# =======================
# Default Fabric settings
# =======================
def env_init(name):
    """
    Initialize a new environment with default settings.
    
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
            'active' : None,
        }

    if name not in env.ENVIRONMENTS:
        env.ENVIRONMENTS['defs'][name] = {
            'roledefs' : {
                'web' : [],
                'db' : [],
                'backend' : [],
            },
            'settings' : {
                'tasks' : {
                    'bootstrap' : ['python_prepare', 'selinux_prepare', 'mysql_prepare', 'apache_prepare'],
                    'install' : ['mysql_createdb', 'apache_configure', 'invenio_install', 'invenio_configure', 'libreoffice_prepare', 'apache_restart', 'crontab_install'],
                    'deploy' : ['invenio_deploy', 'apache_restart'],
                    'clean' : ['crontab_uninstall', 'bibsched_halt', 'apache_clean', 'apache_restart', 'python_clean', 'mysql_dropdb', 'invenio_clean', ],
                    'copy' : [_copy_not_supported],
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
                'copy' : {
                    'from_env' : None,
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
    return (env.ENVIRONMENTS['defs'][name]['roledefs'], env.ENVIRONMENTS['defs'][name]['settings'])


def env_setactive(name):
    """
    Activate an environment (so env_settings will return values from this env).
    
    If name is None, the current active environment will be deactivated.
    """
    try:
        if name:
            env.roledefs = env.ENVIRONMENTS['defs'][name]['roledefs']
            env.ENV_SETTINGS = env.ENVIRONMENTS['defs'][name]['settings']
            env.ENVIRONMENTS['active'] = name
        else:
            env.roledefs = {}
            env.ENV_SETTINGS = {}
            env.ENVIRONMENTS['active'] = None
    except KeyError:
        abort("Cannot activate environment %s - it is not defined." % name)


def env_active():
    """
    Get name of the active environment
    """
    try:
        return env.ENVIRONMENTS['active']
    except AttributeError:
        return None

def env_loaded(name):
    """
    Determine if an environment has been loaded.
    """
    try:
        return name in env.ENVIRONMENTS['defs']
    except (KeyError, AttributeError):
        return False


def env_load(name):
    """
    Load an environment without activating it.
    
    Only environments without any parameters can be loaded.
    """
    if not env_loaded(name):
        if name not in state.commands:
            abort("Environment %s not found" % name)

        # Get the current active environment
        current_env = env_active()

        env_load_func = state.commands[name]
        env_load_func()

        # Reactivate current environment
        env_setactive(current_env)


def env_settings(module, envname = None):
    """
    Get settings for a particular module.
    
    Example (get 'conffile' setting for 'invenio' module)::
    
      conffile = env_settings('invenio')['conffile']
    """
    try:
        if not envname:
            return env.ENV_SETTINGS[module]
        else:
            if envname not in env.ENVIRONMENTS['defs'][envname]:
                env_load(envname)
            return env.ENVIRONMENTS['defs'][envname]['settings'][module]
    except KeyError:
        if envname:
            abort("Misconfiguration - module %s or environment %s not found." % (module, envname))
        else:
            abort("Misconfiguration - module %s not found." % module)
    except AttributeError:
        abort("No environment loaded.")
