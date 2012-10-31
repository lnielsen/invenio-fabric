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
Task for creating and installing a Python virtual environment.
"""

from fabric.api import task, puts, env, local, abort
from fabric.contrib.console import confirm
from fabric.colors import red, cyan
from inveniofab.utils import write_template, python_version
import os


@task
def venv_requirements():
    """ Install Python requirements """
    if 'REQUIREMENTS' not in env:
        puts(cyan(">>> No requirements defined..."))
        return

    puts(cyan(">>> Installing requirements..." % env))

    pyver = python_version()

    for reqfile in env.REQUIREMENTS:
        reqfile = reqfile % env
        reqpath = os.path.join(env.CFG_INVENIO_PREFIX, os.path.basename(reqfile))
        
        ctx = {'reqpath': reqpath, 'reqfile': reqfile, 'pyver': pyver}
        ctx.update(env)

        puts(">>> Writing requirements to %(reqpath)s ..." % ctx)
        write_template(reqpath, ctx, tpl_file=reqfile)

        puts(">>> Installing requirements from %(reqpath)s ..." % ctx)
        cmds = [env.ACTIVATE] if env.WITH_VIRTUALENV else []
        cmds.append("pip install -r %(reqpath)s")
        local(" && ".join(cmds) % ctx)


@task
def venv_dump():
    """ Archive a virtualenv """
    puts(cyan(">>> Creating archive of virutalenv in %(CFG_INVENIO_PREFIX)s..." % env))

    ctx = {
        'dirname' : os.path.dirname(env.CFG_INVENIO_PREFIX),
        'basename' : os.path.basename(env.CFG_INVENIO_PREFIX),
    }

    archive_file = "%(dirname)s/%(basename)s.tar.gz" % ctx
    if os.path.exists(archive_file):
        res = confirm("Existing archive already exists - remove?")
        if not res:
            abort(red("Cannot continue") % env)
        else:
            local("rm -Rf %s" % archive_file)

    cmds = [
        "cd %(dirname)s",
        "tar -cvzf %(basename)s.tar.gz %(basename)s",
    ]
    local(" && ".join(cmds) % ctx)


@task
def venv_load():
    """ Load an archived virtualenv """
    puts(cyan(">>> Loading archived virutalenv..."))

    ctx = {
        'dirname' : os.path.dirname(env.CFG_INVENIO_PREFIX),
        'basename' : os.path.basename(env.CFG_INVENIO_PREFIX),
    }

    archive_file = "%(dirname)s/%(basename)s.tar.gz" % ctx
    if not os.path.exists(archive_file):
        abort(red("Archived virtualenv does not exists - cannot continue") % env)

    # Remove previous installation
    if os.path.exists(env.CFG_INVENIO_PREFIX):
        res = confirm("Remove installation in %(CFG_INVENIO_PREFIX)s ?" % env)
        if not res:
            abort(red("Cannot continue") % env)
        else:
            local("sudo rm -Rf %(CFG_INVENIO_PREFIX)s" % env)

    cmds = [
        "cd %(dirname)s",
        "tar -xvzf %(basename)s.tar.gz",
    ]
    local(" && ".join(cmds) % ctx)


@task
def venv_create():
    """ Create virtualenv environment """
    # Checks
    if 'CFG_INVENIO_PREFIX' not in env:
        abort(red("CFG_INVENIO_PREFIX is not specified in env.") % env)

    puts(cyan(">>> Creating virutalenv in %(CFG_INVENIO_PREFIX)s..." % env))

    # Remove previous installation
    if os.path.exists(env.CFG_INVENIO_PREFIX):
        res = confirm("Remove installation in %(CFG_INVENIO_PREFIX)s ?" % env)
        if not res:
            abort(red("Cannot continue") % env)
        else:
            local("sudo rm -Rf %(CFG_INVENIO_PREFIX)s" % env)

    # Create virtual environment
    dirname = os.path.dirname(env.CFG_INVENIO_PREFIX)
    basename = os.path.basename(env.CFG_INVENIO_PREFIX)

    local("mkdir -p %s" % dirname)
    local("cd %s && virtualenv -p %s %s" % (dirname, env.PYTHON, basename))

    # Create needed symboic links
    pyver = python_version()
    local("mkdir -p %(CFG_INVENIO_PREFIX)s/lib/python/invenio" % env)
    local(("mkdir -p %(CFG_INVENIO_PREFIX)s/lib/python" + pyver + "/site-packages") % env)
    local(("ln -s %(CFG_INVENIO_PREFIX)s/lib/python/invenio %(CFG_INVENIO_PREFIX)s/lib/python" + pyver + "/site-packages/invenio") % env)

    # Write extras into the activate script
    write_template(os.path.join(env.CFG_INVENIO_PREFIX, 'bin/activate'), env, tpl_file='activate-profile.tpl', append=True, mark="ACTIVATE_PROFILE")

    # Install devscripts
    if env.WITH_DEVSCRIPTS:
        puts(">>> Installing invenio-devscripts...")
        local("cd %(CFG_INVENIO_PREFIX)s && git clone https://github.com/tiborsimko/invenio-devscripts.git" % env)
        local("cd %(CFG_INVENIO_PREFIX)s && mv invenio-devscripts/* bin/" % env)
    
    if env.WITH_WORKDIR:
        puts(">>> Installing git-new-workdir...")
        local('wget -O %(CFG_INVENIO_PREFIX)s/bin/git-new-workdir "http://repo.or.cz/w/git.git/blob_plain/HEAD:/contrib/workdir/git-new-workdir"' % env)
        local("chmod +x %(CFG_INVENIO_PREFIX)s/bin/git-new-workdir" % env)

    # OpenOffice temporary directory
    local("mkdir -p %(CFG_INVENIO_PREFIX)s/var/tmp/ooffice-tmp-files" % env)
    local("sudo chown -R nobody %(CFG_INVENIO_PREFIX)s/var/tmp/ooffice-tmp-files" % env)
    local("sudo chmod -R 755 %(CFG_INVENIO_PREFIX)s/var/tmp/ooffice-tmp-files" % env)


@task
def venv_drop():
    """ Drop virtualenv environment """
    # Checks
    if 'CFG_INVENIO_PREFIX' not in env:
        abort(red("CFG_INVENIO_PREFIX is not specified in env.") % env)

    puts(cyan(">>> Dropping virutalenv in %(CFG_INVENIO_PREFIX)s..." % env))

    # Remove previous installation
    if os.path.exists(env.CFG_INVENIO_PREFIX):
        res = confirm("Remove installation in %(CFG_INVENIO_PREFIX)s ?" % env)
        if not res:
            abort(red("Cannot continue") % env)
        else:
            local("sudo rm -Rf %(CFG_INVENIO_PREFIX)s" % env)
    else:
        puts(">>> Nothing to remove - %(CFG_INVENIO_PREFIX)s does not exists..." % env)

