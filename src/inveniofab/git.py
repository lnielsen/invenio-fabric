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
Task for checking out source code from a repository, and running configure,
make on it.
"""

from fabric.api import task, puts, env, settings, local, abort, hide
from fabric.contrib.console import confirm
from fabric.colors import cyan, red
import os

#
# Tasks
#

@task
def repo_configure(repo):
    """ Configure repository """
    topsrcdir = repo_check(repo, workdir=True)

    puts(cyan(">>> Configuring repository: %s ..." % repo))

    ctx = {
        'topsrcdir': topsrcdir,
    }
    ctx.update(env)

    _run_hook(repo, 'configure_hook', default_configure_hook, ctx)


@task
def repo_make(repo, *targets):
    """ Run make in repository """
    topsrcdir = repo_check(repo, workdir=True)

    if not targets:
        try:
            targets = dict(env.CFG_INVENIO_REPOS)[repo]['targets']
        except KeyError:
            abort(red("No default targets found for repository %s" % repo))

    puts(cyan(">>> Running make for %s targets: %s ..." % (repo, " ".join(targets))))

    ctx = {
        'topsrcdir': topsrcdir,
        'targets' : " ".join(targets),
    }
    ctx.update(env)

    local("cd %(topsrcdir)s && make %(targets)s" % ctx)


@task
def repo_install(repo=None, targets_key='install_targets'):
    """ Run configure and make """
    repo_all_configure_make(repo, targets_key)


@task
def repo_prepare(repo=None):
    """ Prepare source code after fresh checkout """
    topsrcdir = repo_check(repo, workdir=True)

    ctx = {'topsrcdir': topsrcdir}
    ctx.update(env)

    _run_hook(repo, 'prepare_hook', default_prepare_hook, ctx)


@task
def repo_setup(repo, ref):
    """ Clone repository """
    puts(cyan(">>> Setting up repository %s with ref %s..." % (repo, ref)))

    topsrcdir = repo_check(repo, check_path=False, workdir=False)
    workdir = repo_check(repo, check_path=False, workdir=True)
    gitdir = os.path.join(topsrcdir, '.git')

    if not os.path.exists(env.CFG_SRCDIR):
        res = confirm("Create repository root %s?" % env.CFG_SRCDIR)
        if not res:
            abort(red("Cannot continue") % env)
        else:
            local("mkdir -p %s" % env.CFG_SRCDIR)

    if not os.path.exists(gitdir) and os.path.exists(topsrcdir):
        res = confirm("Remove %s (it does not seem to be a git repository)?" % topsrcdir)
        if not res:
            abort(red("Cannot continue") % env)
        else:
            local("rm -Rf %s" % topsrcdir)

    if not os.path.exists(gitdir):
        git_clone(repo)
    if not os.path.exists(workdir):
        git_newworkdir(repo)
    git_checkout(repo, ref)
    repo_prepare(repo)


@task
def repo_update(**kwargs):
    """ Pull repository updates """
    # Check repositories to update/setup
    repo_refs = []
    for repo, info in env.CFG_INVENIO_REPOS:
        if repo in kwargs:
            ref = kwargs[repo]
            if not ref:
                ref = None
            repo_refs.append((repo, ref))
            del kwargs[repo]
        else:
            try:
                ref = info['ref']
            except KeyError:
                ref = None
            repo_refs.append((repo, ref))

    if kwargs:
        for repo, ref in kwargs.items():
            abort(red("Invalid repository %s" % repo))

    # Run update
    for repo, ref in repo_refs:
        topsrcdir = repo_check(repo, check_path=False, workdir=True)
        gitdir = os.path.join(topsrcdir, '.git')

        if not os.path.exists(gitdir):
            repo_setup(repo, ref)
        else:
            if ref:
                puts(cyan(">>> Updating repository %s to ref %s..." % (repo, ref)))
                git_fetch(repo)
                git_checkout(repo, ref)
            else:
                commit_id = git_describe(repo)
                puts(cyan(">>> No ref specified for repository %s (currently at HEAD, commit %s) ..." % (repo, commit_id)))

#
# Helpers
#

def repo_check(repo, check_path=True, workdir=False):
    all_repos = [x[0] for x in env.CFG_INVENIO_REPOS]

    if repo not in all_repos:
        abort(red("%s is not a valid repository." % repo))

    repo_path = os.path.join(env.CFG_SRCWORKDIR if workdir and env.WITH_WORKDIR
                             else env.CFG_SRCDIR, repo)

    if check_path and not os.path.exists(repo_path):
        abort(red("Repository does not exists %s" % repo_path))

    return repo_path


def repo_all_configure_make(repo, target_key):
    if repo:
        repo_check(repo)
        repos = [(repo, dict(env.CFG_INVENIO_REPOS)[repo])]
    else:
        repos = env.CFG_INVENIO_REPOS

    for r, info in repos:
        repo_configure(r)

    for r, info in repos:
        try:
            repo_make(r, *info[target_key])
        except KeyError:
            repo_make(r, *['all', 'install'])

#
# Git helpers
#

def git_describe(repo):
    topsrcdir = repo_check(repo, workdir=True)
    version_gen = os.path.join(topsrcdir, 'git-version-gen')

    if os.path.exists(version_gen):
        output = local("cd %s; %s" % (topsrcdir, version_gen), capture=True)
    else:
        output = local("cd %s; git describe --always --abbrev=4 HEAD" % topsrcdir, capture=True)
    return output


def git_show_ref(repo):
    topsrcdir = repo_check(repo, workdir=True)
    local("cd %s; git show-ref" % topsrcdir)


def git_reset(repo, ref):
    topsrcdir = repo_check(repo, workdir=True)
    ctx = {
        'topsrcdir': topsrcdir,
        'ref': ref,
    }
    ctx.update(env)
    local("cd %(topsrcdir)s; git reset --hard %(ref)s " % ctx)


def git_newworkdir(repo):
    if env.WITH_WORKDIR and env.CFG_SRCDIR != env.CFG_SRCWORKDIR:
        srcdir = repo_check(repo, workdir=False, check_path=False)
        srcworkdir = repo_check(repo, workdir=True, check_path=False)

        ctx = {
            'srcdir': srcdir,
            'srcworkdir': srcworkdir,
        }
        ctx.update(env)

        local("%(CFG_INVENIO_PREFIX)s/bin/git-new-workdir %(srcdir)s %(srcworkdir)s" % ctx)


def git_isdirty(dir):
    """
    Check working directory for uncommitted changes
    """
    with settings(hide('everything'), warn_only=True):
        output = local("cd %s && git diff-index --exit-code HEAD --" % dir, capture=True)
    return output.return_code != 0


def git_checkout(repo, ref):
    """
    Checkout a specific git reference.
    """
    topsrcdir = repo_check(repo, workdir=True)

    ctx = {
        'topsrcdir': topsrcdir,
        'ref': ref,
    }
    ctx.update(env)

    # Stash uncommited changes
    if git_isdirty(topsrcdir):
        if not confirm("Working directory %(topsrcdir)s contains uncommited changes. Do you want to stash the changes (required to continue)?" % ctx ):
            abort("Cannot continue unless uncommitted changes are stashed")
        else:
            local("cd %(topsrcdir)s; git stash" % ctx)

    local("cd %(topsrcdir)s; git checkout -f %(ref)s" % ctx)


def git_clone(repo):
    topsrcdir = repo_check(repo, check_path=False, workdir=False)

    try:
        repo_url = dict(env.CFG_INVENIO_REPOS)[repo]['repository']
    except KeyError:
        abort(red("Repository URL for %s not defined" % repo))

    basename = os.path.basename(topsrcdir)
    parent = os.path.dirname(topsrcdir)

    if os.path.exists(topsrcdir):
        res = confirm("Remove existing source code in %s ?" % topsrcdir)
        if not res:
            abort(red("Cannot continue") % env)
        else:
            local("rm -Rf %s" % topsrcdir)
    else:
        if not os.path.exists(parent):
            local("mkdir -p %s" % parent)

    ctx = {
        'basename': basename,
        'parent': parent,
        'topsrcdir': topsrcdir,
        'url': repo_url,
    }

    local("cd %(parent)s; git clone %(url)s %(basename)s " % ctx)


def git_fetch(repo):
    topsrcdir = repo_check(repo)
    local("cd %s; git fetch origin" % topsrcdir)


#
# Helpers
#
def _run_hook(repo, hook_name, default_hook, *args, **kwargs):
    """
    Execute a hook for a given repository. If no hook exists, run the default
    hook.
    """
    try:
        hook = dict(env.CFG_INVENIO_REPOS)[repo][hook_name]
    except KeyError:
        hook = default_hook

    if hook:
        puts(">>> Running hook %s" % hook.__name__)
        hook(*args, **kwargs)
    else:
        puts(">>> No hook found for %s" % hook_name)

#
# Built-in hooks
#
def default_configure_hook(ctx):
    """
    Default way to configure a repo. Assumes repo has a configure script.
    """
    if os.path.exists(os.path.join(ctx['topsrcdir'], "configure")):
        with settings(warn_only=True):
            local("cd %(topsrcdir)s && make -s clean" % ctx)
    local("cd %(topsrcdir)s && ./configure --prefix=%(CFG_INVENIO_PREFIX)s "
          "--with-python=%(CFG_INVENIO_PREFIX)s/bin/python" % ctx)
    local("cd %(topsrcdir)s && make -s clean" % ctx)


def default_prepare_hook(ctx):
    """
    Default way to prepare source code which uses autotools.
    """
    if os.path.exists(os.path.join(ctx['topsrcdir'], "configure.ac")):
        local("cd %(topsrcdir)s; aclocal && automake -a && autoconf -f" % ctx)
