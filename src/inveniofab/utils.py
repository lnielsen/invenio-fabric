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

from fabric.api import prompt, env, abort, warn, get, put, roles, task, execute
from fabric.api import local as fab_local, run as fab_run, sudo as fab_sudo
from fabric.colors import red
from fabric.contrib.files import exists as fab_exists, append as fab_append
from jinja2 import Environment, FileSystemLoader
from jinja2.exceptions import TemplateNotFound
import getpass
import os
import re
from StringIO import StringIO


def is_local():
    """ Determine if env.host is localhost """
    return (env.host in ['localhost', '127.0.0.1'] or env.host is None)


def run_local(command, shell=True, pty=True, combine_stderr=True, capture=False):
    """ run/local function based on host """
    if is_local():
        return fab_local(command, capture=capture)
    else:
        return fab_run(command, shell=shell, pty=pty, combine_stderr=combine_stderr)


def sudo_local(command, shell=True, pty=True, combine_stderr=True, user=None, capture=False):
    """ sudo/local function based on host """
    if env.user == user:
        return run_local(command, shell=shell, pty=pty, combine_stderr=combine_stderr, capture=capture)
    else:
        if is_local():
            return fab_local("sudo %s" % command, capture=capture)
        else:
            return fab_sudo(command, shell=shell, pty=pty, combine_stderr=combine_stderr, user=user)


def exists_local(path, use_sudo=False, verbose=False):
    if is_local():
        return os.path.exists(path)
    else:
        return fab_exists(path, use_sudo=use_sudo, verbose=verbose)


def prompt_and_check(questions, check_func, cache_key=None, stored_answers=None):
    """
    Ask user for questions, and check answers with supplied function
    """
    done = False

    if stored_answers:
        if check_func(stored_answers):
            answers = stored_answers
            done = True

    if cache_key and cache_key in env.get('answers_cache', {}):
        return env.answers_cache[cache_key]

    while not done:
        answers = {}
        for q, key in questions:
            if 'password' in key:
                answers[key] = getpass.getpass(q + " ")
            else:
                answers[key] = prompt(q)
        if check_func(answers):
            done = True

    if cache_key:
        if 'answers_cache' not in env:
            env.answers_cache = {}
        env.answers_cache[cache_key] = answers
    return answers


def write_template(filename, context, tpl_str=None, tpl_file=None, remote_tpl_file=None, append=False, mark=None, use_sudo=False):
    """
    Render template and write output to file

    @param filename: File to write
    @param template: Name of template
    @param context: Dictionary for the template context (usually just env)
    @param append: bool, True if you want to append content to file instead of overwriting.
    @param mark: str, If append is true and mark is defined, then the rendered
                 template will replace any previous appened version.
    """
    # If we're in local mode, interpret remote_tpl_file as it was a local file.
    if is_local() and remote_tpl_file:
        tpl_file = remote_tpl_file
        remote_tpl_file = None

    if remote_tpl_file:
        f = StringIO()
        get(remote_tpl_file, f)
        tpl = env.jinja.from_string(f.getvalue())
        f.close()
    if tpl_file:
        try:
            tpl = env.jinja.get_template(tpl_file)
        except TemplateNotFound:
            jinja = Environment(loader=FileSystemLoader([os.path.dirname(tpl_file)]))
            tpl = jinja.get_template(os.path.basename(tpl_file))
    elif tpl_str:
        tpl = env.jinja.from_string(tpl_str)
    content = tpl.render(context)

    if append and mark is not None:
        start_mark = "### START: %s ###" % mark
        end_mark = "### END: %s ###" % mark
        marked_content = """%s\n%s\n%s\n""" % (start_mark, content, end_mark)

        file_content = []
        skip = False
        added = False

        if is_local():
            f = open(filename, 'r')
        else:
            f = StringIO()
            get(filename, f)

        for line in f:
            if line == start_mark:
                skip = True
                added = True
                file_content.append(marked_content)
            elif line == end_mark:
                skip = False
            else:
                if not skip:
                    file_content.append(line)
        f.close()

        if added:
            append = False
            content = "\n".join(file_content)
        else:
            content = marked_content

    if is_local():
        f = open(filename, 'a' if append else 'w')
        f.write(content.encode('utf8'))
        f.close()
    else:
        if append:
            fab_append(filename, content.encode('utf8'), use_sudo=use_sudo)
        else:
            put(StringIO(content.encode('utf8')), filename, use_sudo=use_sudo)


def python_version():
    """ Determine Python version """
    return run_local(("%(CFG_INVENIO_PREFIX)s/bin/python -c \"import sys;print str(sys.version_info[0]) + '.' + str(sys.version_info[1])\"") % env, capture=True)


def pythonbrew_versions():
    """ Get all installed Pythonbrew versions """
    pythonsdir = os.path.join(os.environ.get('PYTHONBREW_ROOT',
                          os.path.expanduser('~/.pythonbrew')), 'pythons')

    version_dict = {}
    pat = re.compile("Python-(\d\.\d.\d)")

    for d in os.listdir(pythonsdir):
        pydir = os.path.join(pythonsdir, d)
        pybin = os.path.join(pydir, 'bin/python')
        m = pat.match(d)

        if m and os.path.isdir(pydir) and os.path.exists(pybin):
            major, minor, patch = m.group(1).split('.')
            version_dict["%s%s%s" % (major, minor, patch)] = pybin
            version_dict["%s%s" % (major, minor)] = pybin

    return version_dict


def template_hook_factory(tpl_file, filename, warn_only=True):
    """
    Factory method for generating hook functions that renders a template,
    and writes it to a specific location.

    Filename may include string replacement like e.g. %(CFG_INVENIO_PREFIX)s.
    """
    def write_template_hook(ctx):
        try:
            write_template(filename % ctx, ctx, tpl_file=tpl_file)
        except TemplateNotFound:
            if warn_only:
                warn(red("Couldn't find template %s" % tpl_file))
            else:
                abort(red("Couldn't find template %s" % tpl_file))

    return write_template_hook


def _first(f, dirs=['']):
    for d in dirs:
        env_f = os.path.join(d, f)
        if os.path.exists(env_f):
            return (env_f, f)
    abort("File %s not found" % f)


def _upload(fs):
    for local_f, remote_f in fs:
        remote_f = os.path.join(env.CFG_INVENIO_PREFIX, remote_f)
        basedir = os.path.dirname(remote_f)
        if not exists_local(basedir, use_sudo=True):
            sudo_local("mkdir -p %s" % basedir, user=env.CFG_INVENIO_USER)
        if is_local():
            sudo_local("cp %s %s" % (local_f, remote_f), user=env.CFG_INVENIO_USER)
        else:
            put(local_f, remote_f, use_sudo=True)


@task
def upload_files():
    """
    Upload files specified by CFG_FILES
    """
    for role, files in env.get('CFG_FILES', {}).items():
        files = map(lambda f: _first(f, dirs=[env.env_name, 'common']), files)
        execute(_upload, files, role=role)
