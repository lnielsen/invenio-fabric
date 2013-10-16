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

from fabric.api import task, puts, env, local, abort, roles
from fabric.contrib.console import confirm
from fabric.colors import red, cyan
from inveniofab.utils import write_template, python_version, sudo_local, \
    exists_local
import os


@task
@roles('web')
def venv_pyuno_install():
    """
    Install Python OpenOffice binding

    The task will try to locate ``uno.py`` and ``unohelper.py`` in ``/usr/``,
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

    sudo_local("cp  `find /usr/ -name uno.py 2>/dev/null | head -n 1` %(CFG_INVENIO_PREFIX)s/lib/python%(pyver)s/site-packages/" % ctx, user=env.CFG_INVENIO_USER)
    sudo_local("cp `find /usr/ -name unohelper.py 2>/dev/null | head -n 1` %(CFG_INVENIO_PREFIX)s/lib/python%(pyver)s/site-packages/" % ctx, user=env.CFG_INVENIO_USER)


@task
@roles('web')
def venv_libxslt_install():
    """
    Install libxslt into virtualenv
    """
    ctx = {
        'libxslt': 'libxslt-1.1.26',
        'libxslt_ver': '1.1.26',
        'libxslt_path': os.path.join(env.CFG_INVENIO_PREFIX, 'libxslt-1.1.26'),
    }
    ctx.update(env)

    if exists_local(ctx['libxslt_path']):
        sudo_local("rm -Rf %(libxslt_path)s" % ctx, user=env.CFG_INVENIO_USER)
    if exists_local("%(libxslt_path)s.tar.gz" % ctx):
        sudo_local("rm -Rf %(libxslt_path)s.tar.gz" % ctx, user=env.CFG_INVENIO_USER)

    sudo_local("cd %(CFG_INVENIO_PREFIX)s; wget ftp://xmlsoft.org/libxml2/%(libxslt)s.tar.gz; tar -xzf %(libxslt)s.tar.gz" % ctx, user=env.CFG_INVENIO_USER)
    sudo_local("cd %(libxslt_path)s; ./configure --prefix=%(CFG_INVENIO_PREFIX)s --with-python=%(CFG_INVENIO_PREFIX)s/bin/python; make; cd python; make install" % ctx, user=env.CFG_INVENIO_USER)

    sudo_local("rm -Rf %(libxslt_path)s" % ctx, user=env.CFG_INVENIO_USER)
    sudo_local("rm -Rf %(libxslt_path)s.tar.gz" % ctx, user=env.CFG_INVENIO_USER)


@task
@roles('web')
def venv_requirements(upgrade=False):
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
    reqpaths = []

    for repo, reqfile in requirements:
        reqfile = reqfile % env
        reqpath = os.path.join(env.CFG_INVENIO_PREFIX, "%s_%s" % (repo, os.path.basename(reqfile)))

        ctx = {'reqpath': reqpath, 'reqfile': reqfile, 'pyver': pyver, 'upgrade': '--upgrade' if upgrade else ''}
        ctx.update(env)

        puts(">>> Writing requirements to %(reqpath)s ..." % ctx)
        write_template(reqpath, ctx, remote_tpl_file=reqfile, use_sudo=True)
        reqpaths.append(reqpath)

    for reqpath in reqpaths:
        ctx = {'reqpath': reqpath, 'pyver': pyver, 'upgrade': '--upgrade' if upgrade else ''}
        ctx.update(env)
        puts(">>> Installing requirements from %(reqpath)s ..." % ctx)
        cmds = [env.ACTIVATE] if env.WITH_VIRTUALENV else []
        cmds.append("pip install %(upgrade)s -r %(reqpath)s")
        sudo_local(" && ".join(cmds) % ctx, user=env.CFG_INVENIO_USER)


@task
@roles('web')
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
        'dirname': os.path.dirname(env.CFG_INVENIO_PREFIX),
        'basename': os.path.basename(env.CFG_INVENIO_PREFIX),
    }

    archive_file = "%(dirname)s/%(basename)s.tar.gz" % ctx
    if exists_local(archive_file):
        res = confirm("Existing archive already exists - remove?")
        if not res:
            abort(red("Cannot continue") % env)
        else:
            sudo_local("rm -Rf %s" % archive_file, user=env.CFG_INVENIO_USER)

    cmds = [
        "cd %(dirname)s",
        "tar -cvzf %(basename)s.tar.gz %(basename)s",
    ]
    sudo_local(" && ".join(cmds) % ctx, user=env.CFG_INVENIO_USER)


@task
@roles('web')
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
        'dirname': os.path.dirname(env.CFG_INVENIO_PREFIX),
        'basename': os.path.basename(env.CFG_INVENIO_PREFIX),
    }

    archive_file = "%(dirname)s/%(basename)s.tar.gz" % ctx
    if not exists_local(archive_file):
        abort(red("Archived virtualenv does not exists - cannot continue") % env)

    # Remove previous installation
    if exists_local(env.CFG_INVENIO_PREFIX):
        res = confirm("Remove installation in %(CFG_INVENIO_PREFIX)s ?" % env)
        if not res:
            abort(red("Cannot continue") % env)
        else:
            sudo_local("rm -Rf %(CFG_INVENIO_PREFIX)s" % env)

    cmds = [
        "cd %(dirname)s",
        "tar -xvzf %(basename)s.tar.gz",
    ]
    sudo_local(" && ".join(cmds) % ctx, user=env.CFG_INVENIO_USER)


@task
@roles('web')
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
    if exists_local(env.CFG_INVENIO_PREFIX):
        res = confirm("Remove installation in %(CFG_INVENIO_PREFIX)s ?" % env)
        if not res:
            abort(red("Cannot continue") % env)
        else:
            sudo_local("rm -Rf %(CFG_INVENIO_PREFIX)s" % env)

    # Create virtual environment
    dirname = os.path.dirname(env.CFG_INVENIO_PREFIX)
    basename = os.path.basename(env.CFG_INVENIO_PREFIX)

    sudo_local("mkdir -p %s" % dirname, user=env.CFG_INVENIO_USER)
    if confirm("Create %(CFG_INVENIO_PREFIX)s with sudo?" % env):
        sudo_local("mkdir -p %(CFG_INVENIO_PREFIX)s" % env)
        sudo_local("chown %(CFG_INVENIO_USER)s:%(CFG_INVENIO_USER)s %(CFG_INVENIO_PREFIX)s" % env)
    sudo_local("cd %s && virtualenv -p %s %s" % (dirname, env.PYTHON, basename), user=env.CFG_INVENIO_USER)

    # Create needed symboic links
    pyver = python_version()
    sudo_local("mkdir -p %(CFG_INVENIO_PREFIX)s/lib/python/invenio" % env, user=env.CFG_INVENIO_USER)
    sudo_local(("mkdir -p %(CFG_INVENIO_PREFIX)s/lib/python" + pyver + "/site-packages") % env, user=env.CFG_INVENIO_USER)
    sudo_local(("ln -s %(CFG_INVENIO_PREFIX)s/lib/python/invenio %(CFG_INVENIO_PREFIX)s/lib/python" + pyver + "/site-packages/invenio") % env, user=env.CFG_INVENIO_USER)

    # Write extras into the activate script
    write_template(os.path.join(env.CFG_INVENIO_PREFIX, 'bin/activate'), env, tpl_file='activate-profile.tpl', append=True, mark="ACTIVATE_PROFILE", use_sudo=True)

    # Install devscripts
    if env.WITH_DEVSCRIPTS:
        puts(">>> Installing invenio-devscripts...")
        sudo_local("cd %(CFG_INVENIO_PREFIX)s && git clone https://github.com/tiborsimko/invenio-devscripts.git" % env, user=env.CFG_INVENIO_USER)
        sudo_local("cd %(CFG_INVENIO_PREFIX)s && mv invenio-devscripts/* bin/" % env, user=env.CFG_INVENIO_USER)

    if env.WITH_WORKDIR:
        puts(">>> Installing git-new-workdir...")
        sudo_local('wget -O %(CFG_INVENIO_PREFIX)s/bin/git-new-workdir "http://repo.or.cz/w/git.git/blob_plain/HEAD:/contrib/workdir/git-new-workdir"' % env, user=env.CFG_INVENIO_USER)
        sudo_local("chmod +x %(CFG_INVENIO_PREFIX)s/bin/git-new-workdir" % env, user=env.CFG_INVENIO_USER)

    # OpenOffice temporary directory
    sudo_local("mkdir -p %(CFG_INVENIO_PREFIX)s/var/tmp/ooffice-tmp-files" % env, user=env.CFG_INVENIO_USER)
    sudo_local("sudo chown -R nobody %(CFG_INVENIO_PREFIX)s/var/tmp/ooffice-tmp-files" % env)
    sudo_local("sudo chmod -R 755 %(CFG_INVENIO_PREFIX)s/var/tmp/ooffice-tmp-files" % env)


@task
@roles('web')
def venv_drop():
    """ Drop virtualenv environment """
    # Checks
    if 'CFG_INVENIO_PREFIX' not in env:
        abort(red("CFG_INVENIO_PREFIX is not specified in env.") % env)

    puts(cyan(">>> Dropping virtualenv in %(CFG_INVENIO_PREFIX)s..." % env))

    # Remove previous installation
    if exists_local(env.CFG_INVENIO_PREFIX):
        res = confirm("Remove installation in %(CFG_INVENIO_PREFIX)s ?" % env)
        if not res:
            abort(red("Cannot continue") % env)
        else:
            sudo_local("sudo rm -Rf %(CFG_INVENIO_PREFIX)s" % env)
    else:
        puts(">>> Nothing to remove - %(CFG_INVENIO_PREFIX)s does not exists..." % env)
