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
Tasks for creating and installing Python virtual environments.

All task works on local system.
"""

from fabric.api import task, puts, env, local, abort
from fabric.contrib.console import confirm
from fabric.colors import red, cyan
from inveniofab.utils import write_template, python_version
import os


@task
def venv_pyuno_install():
    """
    Install Python OpenOffice binding

    The tassk will try to locate ``uno.py`` and ``unohelper.py`` in ``/usr/``,
    and copy it to your virtualenv's site-packages.

    .. warning::
      
       The Python OpenOffice bindings from your system is specific to
       your system's Python interpreter, hence if your system Python is 2.7 and 
       you are installing the bindings into virtualenv with Python 2.4, the 
       bindings will not work.
    """
    pyver = python_version()
    ctx = {'pyver': pyver}
    ctx.update(env)

    local("cp  `find /usr/ -name uno.py 2>/dev/null | head -n 1` %(CFG_INVENIO_PREFIX)s/lib/python%(pyver)s/site-packages/" % ctx)
    local("cp `find /usr/ -name unohelper.py 2>/dev/null | head -n 1` %(CFG_INVENIO_PREFIX)s/lib/python%(pyver)s/site-packages/" % ctx)


@task
def venv_requirements():
    """
    Install Python packages
    
    The task will install Python packages defined in PIP requirements file.
    """
    requirements = []
    for repo, info in env.CFG_INVENIO_REPOS:
        requirements.extend([(repo, x) for x in info.get('requirements', [])])

    if not requirements:
        puts(cyan(">>> No requirements defined..."))
        return

    puts(cyan(">>> Installing requirements..." % env))

    pyver = python_version()

    for repo, reqfile in requirements:
        reqfile = reqfile % env
        reqpath = os.path.join(env.CFG_INVENIO_PREFIX, "%s_%s" % (repo, os.path.basename(reqfile)))

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
    """
    Archive a virtualenv
    
    The task will create an archive ``<virtualenv name>.tar.gz`` of the entire
    virtual environment. If an existing archive already exists, the user will
    be asked for confirmation to remove it. Normally this command is invoked
    indirectly via the compound task :meth:`inveniofab.compound.dump` which 
    takes care of dumping the database prior to archiving the virtual 
    environment.
    """
    puts(cyan(">>> Creating archive of virtualenv in %(CFG_INVENIO_PREFIX)s..." % env))

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
    """
    Load an archived virtualenv
    
    The task will extract an archived virtual environment created with 
    :meth:`~venv_dump`. Normally this command is invoked
    indirectly via the compound task :meth:`inveniofab.compound.load` which 
    takes care of loading the database after extracting the virtual 
    environment.
    """
    puts(cyan(">>> Loading archived virtualenv..."))

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
    """
    Create virtualenv environment
    
    The virtualenv is created in ``env.CFG_INVENIO_PREFIX``, and will also
    create ``lib/python/invenio/`` and symlink it the virtualenv's 
    site-packages, as well as ``var/tmp/ooffice-tmp-files`` (via sudo). If 
    ``env.WITH_DEVSCRIPTS`` is ``True``, invenio-devscripts will be installed. 
    If ``env.WITH_WORKDIR`` is ``True`` git-new-workdir will be installed.
    
    Lastly, it will append render the template ``activate-profile.tpl`` and
    append it to ``bin/activate``. The script will setup common needed
    environment variables that e.g. invenio-devscripts depend on.
    
    If an existing environment already exists, the user will be asked for
    confirmation to remove the directory (using sudo, due to the directory
    ``var/tmp/ooffice-tmp-files`` which is created using sudo).
    """
    # Checks
    if 'CFG_INVENIO_PREFIX' not in env:
        abort(red("CFG_INVENIO_PREFIX is not specified in env.") % env)

    puts(cyan(">>> Creating virtualenv in %(CFG_INVENIO_PREFIX)s..." % env))

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

    puts(cyan(">>> Dropping virtualenv in %(CFG_INVENIO_PREFIX)s..." % env))

    # Remove previous installation
    if os.path.exists(env.CFG_INVENIO_PREFIX):
        res = confirm("Remove installation in %(CFG_INVENIO_PREFIX)s ?" % env)
        if not res:
            abort(red("Cannot continue") % env)
        else:
            local("sudo rm -Rf %(CFG_INVENIO_PREFIX)s" % env)
    else:
        puts(">>> Nothing to remove - %(CFG_INVENIO_PREFIX)s does not exists..." % env)

