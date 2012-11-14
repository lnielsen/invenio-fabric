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

"""
Task to work with devserver
"""

from fabric.api import task, puts, env, local, warn
from fabric.colors import cyan, red
from inveniofab.utils import write_template, python_version
from jinja2.exceptions import TemplateNotFound
import os
import stat

@task
def devserver_conf():
    """ 
    Render and update invenio-devserver configuration

    The task will look for the template ``config_local.py.tpl``, and render and
    write it to ``config_local.py`` in the virtual environments site-packages.
    
    The invenio-devserver install two commands:
    
      * ``serve`` - Invenio development server based on Werkzeug.
      * ``mailserve`` - Debug mail server which will print all emails to the console.
    
    .. note::
    
        The invenio-devserver works with the non-Flask based versions of Invenio. 
        Also, the invenio-devserver is only installed if ``env.WITH_DEVSERVER`` is
        ``True``.
    
    .. seealso::
    
       See also invenio-devserver for further information on the content of
       ``config_local.py.tpl``: https://bitbucket.org/osso/invenio-devserver
    """
    puts(cyan(">>> Configuring invenio-devserver..." % env))

    pyver = python_version()

    local_file = 'config_local.py.tpl'
    local_remote = os.path.join(env.CFG_INVENIO_PREFIX, 'lib/python%s/site-packages/config_local.py' % pyver)

    puts(">>> Writing config_local.py to %s ..." % local_remote)
    try:
        write_template(local_remote, env, tpl_file=local_file)
    except TemplateNotFound:
        warn(red("Could not find template %s" % local_file))


@task
def devserver_install_flask():
    """
    Install a Flask devserver
    
    The task will look for the template ``rundevserver.py.tpl``, render it and
    write it to ``bin/rundevserver.py``.
    
    To start the Flask development server, run::
    
      (venv)$ rundevserver.py
    
    .. note::
    
       ``rundevserver.py`` only works with Flask based versions of Invenio.
    """
    puts(cyan(">>> Configuring Flask devserver..." % env))
    
    local_file = 'rundevserver.py.tpl'
    local_remote = os.path.join(env.CFG_INVENIO_PREFIX, 'bin/rundevserver.py')

    puts(">>> Writing rundevserver.py to %s ..." % local_remote)
    try:
        write_template(local_remote, env, tpl_file=local_file)
        local("chmod a+x %s" % local_remote)
    except TemplateNotFound:
        warn(red("Could not find template %s" % local_file))
