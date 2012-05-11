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
Utility and helper functions. Functions in this module are not 
meant as standalone Fabric tasks, but for usage in other library
tasks. 
"""

from fabric.api import env, run, sudo, abort, cd
from fabric.contrib.files import exists
from jinja2 import Environment, FileSystemLoader
import os
import re
import tempfile

def source_checkout(path, repo=None, source_dir=None, use_sudo=False):
    """
    Helper function to checkout repository or symlink source directory.
    """
    parent, base = os.path.split(path)

    _run_func = sudo if use_sudo else run

    if exists(path):
        # Path already exists os assume it's the right one.
        return 
    elif not exists(parent):
        abort("Path %s does not exists." % parent)

    with cd(parent):
        if repo:
            _run_func("git clone %s %s" % (repo, base))
        elif source_dir:
            _run_func("ln -s %s %s" % (source_dir, path))
        else:
            abort("Please provide either a repository or a source directory.")


def source_update(path, repo=None, source_dir=None, use_sudo=False):
    """
    Helper function to update source in a repository or source dir.
    """
    _run_func = sudo if use_sudo else run

    with cd(path):
        if repo:
            _run_func("git pull")
        elif source_dir:
            # Source dir is assumed to be updated outside of this task
            # e.g via untar, directly editing etc. 
            pass


def source_clean(path, repo=None, source_dir=None, use_sudo=False):
    """
    Helper function to remove checked out source code
    """
    parent, base = os.path.split(path)

    _run_func = sudo if use_sudo else run

    with cd(parent):
        if repo:
            _run_func("rm -Rf %s" % base)
        elif source_dir:
            # Symlinked directory
            _run_func("rm -f %s" % base)


def slc_version():
    """
    Determine Scientific Linux CERN version 
    """
    if not hasattr(env, 'SLC_VERSION'):
        osver = run("cat /etc/redhat-release")
        m = re.match("Scientific Linux CERN SLC release ([0-9])\.([0-9]) \([A-Za-z-_ ]+\)", osver)
        if m:
            env.SLC_VERSION = (int(m.group(1)), int(m.group(2)))
        else:
            env.SLC_VERSION = (int(m.group(1)), int(m.group(2)))
    return env.SLC_VERSION


def render_file_template( filename, context ):
    """
    Render a template and save it in a temporary file which
    can e.g. be uploaded to a remote host.
    """
    jenv = Environment(loader=FileSystemLoader('.'))
    text = jenv.get_template(filename).render(**context or {})
    
    hdl, tempfilename = tempfile.mkstemp(text=True)
    
    with open(tempfilename, 'w') as f:
        f.write(text.encode('utf8'))
    
    return tempfilename



    
