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
Library tasks for configuring and running MySQL for Invenio.
"""

from __future__ import with_statement
from fabric.api import puts, task, env, local, abort, settings, hide
from fabric.colors import red, cyan
from fabric.contrib.console import confirm
from inveniofab.env import env_get
from inveniofab.utils import prompt_and_check
import os

@task
def mysql_dropdb(stored_answers=None):
    """
    Drop database and user
    """
    with hide('commands'):
        puts(cyan(">>> Dropping database and user ..." % env))

        answers = prompt_and_check([
            ("MySQL admin user:", "user"),
            ("MySQL admin password:", "password")
        ], mysql_admin_check(env.CFG_DATABASE_HOST, env.CFG_DATABASE_PORT),
        cache_key="mysql://%s:%s" % (env.CFG_DATABASE_HOST, env.CFG_DATABASE_PORT),
        stored_answers=stored_answers)

        # Escape quote characters
        answers['password'] = answers['password'].replace("'", "\'").replace('"', '\"').replace('$', '\\$')
        user_pw = '-u %(user)s --password=%(password)s' % answers if answers['password'] else '-u %(user)s' % answers

        ctx = {
            'user_pw': user_pw,
            'host': env.CFG_DATABASE_HOST,
            'name' :  env.CFG_DATABASE_NAME,
            'user' :  env.CFG_DATABASE_USER,
            'password' : env.CFG_DATABASE_PASS,
            'port': env.CFG_DATABASE_PORT,
        }

        ctx['password'] = ctx['password'].replace("'", "\'").replace('"', '\"').replace('$', '\\$')

        local('mysql %(user_pw)s -h %(host)s -P %(port)s -e "DROP DATABASE IF EXISTS %(name)s"' % ctx)
        with settings(warn_only=True):
            local('mysql %(user_pw)s -h %(host)s -P %(port)s -e "REVOKE ALL PRIVILEGES ON %(name)s.* FROM %(user)s@localhost"' % ctx)
        local('mysqladmin %(user_pw)s -h %(host)s -P %(port)s flush-privileges' % ctx)


@task
def mysql_createdb(stored_answers=None):
    """
    Create database and user
    """
    with hide('commands'):
        puts(cyan(">>> Creating database and user ..." % env))

        answers = prompt_and_check([
            ("MySQL admin user:", "user"),
            ("MySQL admin password:", "password")
        ], mysql_admin_check(env.CFG_DATABASE_HOST, env.CFG_DATABASE_PORT),
        cache_key="mysql://%s:%s" % (env.CFG_DATABASE_HOST, env.CFG_DATABASE_PORT),
        stored_answers=stored_answers)

        # Escape quote characters
        answers['password'] = answers['password'].replace("'", "\'").replace('"', '\"').replace('$', '\\$')
        user_pw = '-u %(user)s --password=%(password)s' % answers if answers['password'] else '-u %(user)s' % answers

        ctx = {
            'user_pw': user_pw,
            'host' :  env.CFG_DATABASE_HOST,
            'name' :  env.CFG_DATABASE_NAME,
            'user' :  env.CFG_DATABASE_USER,
            'password' : env.CFG_DATABASE_PASS,
            'port': env.CFG_DATABASE_PORT,
        }

        ctx['password'] = ctx['password'].replace("'", "\'").replace('"', '\"').replace('$', '\\$')

        # Run commands
        local('mysql %(user_pw)s -h %(host)s -P %(port)s -e "CREATE DATABASE IF NOT EXISTS %(name)s DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci"' % ctx)
        local('mysql %(user_pw)s -h %(host)s -P %(port)s -e "GRANT ALL PRIVILEGES ON %(name)s.* TO %(user)s@localhost IDENTIFIED BY \'%(password)s\';"' % ctx)
        local('mysqladmin %(user_pw)s -h %(host)s -P %(port)s flush-privileges' % ctx)


@task
def mysql_dump(outputdir=None):
    """
    Dump database to file
    """
    with hide('commands'):
        puts(cyan(">>> Dumping database ..." % env))

        answers = {
            'user' : env.CFG_DATABASE_USER,
            'password' : env.CFG_DATABASE_PASS,
        }

        # Escape quote characters
        answers['password'] = answers['password'].replace("'", "\'").replace('"', '\"').replace('$', '\\$')

        if not outputdir:
            outputdir = env.CFG_DATABASE_DUMPDIR

        if not os.path.exists(outputdir):
            abort(red("Output directory %s does not exists" % outputdir))

        user_pw = '-u %(user)s --password=%(password)s' % answers if answers['password'] else '-u %(user)s' % answers
        outfile = os.path.join(outputdir, "%s.sql" % env.CFG_DATABASE_NAME)
        outfile_gz = "%s.gz" % outfile

        for f in [outfile, outfile_gz]:
            if os.path.exists(f):
                res = confirm("Remove existing DB dump in %s ?" % f)
                if not res:
                    abort(red("Cannot continue") % env)
                else:
                    local("rm -Rf %s" % f)

        ctx = {
            'user_pw': user_pw,
            'host' :  env.CFG_DATABASE_HOST,
            'name' :  env.CFG_DATABASE_NAME,
            'port': env.CFG_DATABASE_PORT,
            'outfile_gz': outfile_gz,
            'outfile': outfile,
        }

        # Run commands
        local('mysqldump %(user_pw)s -h %(host)s -P %(port)s --skip-opt '
              '--add-drop-table --add-locks --create-options --quick '
              '--extended-insert --set-charset --disable-keys %(name)s '
              '| gzip -c > %(outfile_gz)s' % ctx)


@task
def mysql_load(dumpfile=None, stored_answers=None):
    """
    Load MySQL dump file
    """
    with hide('commands'):
        puts(cyan(">>> Loading database dump..."))

        if not dumpfile:
            dumpfile = os.path.join(env.CFG_DATABASE_DUMPDIR, "%s.sql.gz" % env.CFG_DATABASE_NAME)

        if not os.path.exists(dumpfile):
            abort("File %s does not exists." % dumpfile)

        answers = prompt_and_check([
            ("MySQL admin user:", "user"),
            ("MySQL admin password:", "password")
        ], mysql_admin_check(env.CFG_DATABASE_HOST, env.CFG_DATABASE_PORT),
        cache_key="mysql://%s:%s" % (env.CFG_DATABASE_HOST, env.CFG_DATABASE_PORT),
        stored_answers=stored_answers)

        # Escape quote characters
        answers['password'] = answers['password'].replace("'", "\'").replace('"', '\"').replace('$', '\\$')
        user_pw = '-u %(user)s --password=%(password)s' % answers if answers['password'] else '-u %(user)s' % answers

        if dumpfile.endswith(".gz"):
            dumpfile_stream = "gunzip -c %s" % dumpfile
        else:
            dumpfile_stream = "cat %s" % dumpfile

        ctx = {
            'user_pw': user_pw,
            'host' :  env.CFG_DATABASE_HOST,
            'name' :  env.CFG_DATABASE_NAME,
            'user' :  env.CFG_DATABASE_USER,
            'password' : env.CFG_DATABASE_PASS,
            'port': env.CFG_DATABASE_PORT,
            'dumpfile': dumpfile,
            'dumpfile_stream': dumpfile_stream,
        }

        # Escape quote characters
        ctx['password'] = ctx['password'].replace("'", "\'").replace('"', '\"').replace('$', '\\$')

        if confirm("This will erease all data in the existing database. Are you sure you want to load %(dumpfile)s?" % ctx):
            mysql_dropdb(stored_answers=answers)
            mysql_createdb(stored_answers=answers)

            local('%(dumpfile_stream)s | mysql %(user_pw)s -h %(host)s -P %(port)s -f %(name)s' % ctx)

        return dumpfile


@task
def mysql_copy(from_env):
    """
    Copy database from latest available dump.

    Currently it is assumed that the dump file is accessible on the
    same path on both environment host systems. This usually means that
    the dumps are stored on a shared network storage.
    """
    with hide('commands'):
        to_env = env
        from_env = env_get(from_env)

        answers_from = prompt_and_check([
            ("FROM MySQL admin user:", "user"),
            ("FROM MySQL admin password:", "password")
        ], mysql_admin_check(from_env.CFG_DATABASE_HOST, from_env.CFG_DATABASE_PORT))

        answers_to = prompt_and_check([
            ("TO MySQL admin user:", "user"),
            ("TO MySQL admin password:", "password")
        ], mysql_admin_check(to_env.CFG_DATABASE_HOST, to_env.CFG_DATABASE_PORT))

        # Escape quote characters
        answers_from['password'] = answers_from['password'].replace("'", "\'").replace('"', '\"').replace('$', '\\$')
        answers_to['password'] = answers_to['password'].replace("'", "\'").replace('"', '\"').replace('$', '\\$')

        user_pw_from = '-u %(user)s --password=%(password)s' % answers_from if answers_from['password'] else '-u %(user)s' % answers_from
        user_pw_to = '-u %(user)s --password=%(password)s' % answers_to if answers_to['password'] else '-u %(user)s' % answers_to

        ctx = {
            'user_pw_from': user_pw_from,
            'user_pw_to': user_pw_to,
            'from_host' :  from_env.CFG_DATABASE_HOST,
            'from_name' :  from_env.CFG_DATABASE_NAME,
            'from_user' :  from_env.CFG_DATABASE_USER,
            'from_password' : from_env.CFG_DATABASE_PASS,
            'from_port': from_env.CFG_DATABASE_PORT,
            'to_host' :  to_env.CFG_DATABASE_HOST,
            'to_name' :  to_env.CFG_DATABASE_NAME,
            'to_user' :  to_env.CFG_DATABASE_USER,
            'to_password' : to_env.CFG_DATABASE_PASS,
            'to_port': to_env.CFG_DATABASE_PORT,
        }


        puts(">>> You are about to copy:")
        puts(">>>   %(from_user)s@%(from_host)s:%(from_port)s/%(from_name)s" % ctx)
        puts(">>> to:")
        puts(">>>   %(to_user)s@%(to_host)s:%(to_port)s/%(to_name)s" % ctx)

        if confirm("This will erease all data in the latter database and may impact performance on system being copied from. Are you sure you want to proceed?"):
            mysql_dropdb(stored_answers=answers_to)
            mysql_createdb(stored_answers=answers_to)

        local('mysqldump %(user_pw_from)s -h %(from_host)s -P %(from_port)s -f %(from_name)s | mysql %(user_pw_to)s -h %(to_host)s -P %(to_port)s -f %(to_name)s' % ctx)


#
# Helpers
#

def mysql_admin_check(host, port):
    def _mysql_admin_check(answers):
        ctx = {'host': host, 'port': port}
        ctx.update(answers)
        try:
            if answers['password']:
                res = local("""mysql -u %(user)s --password=%(password)s -h %(host)s -P %(port)s -e 'SELECT 1'""" % ctx)
            else:
                res = local("""mysql -u %(user)s -h %(host)s -P %(port)s -e 'SELECT 1'""" % ctx)

            return True
        except SystemExit:
            puts(red("MySQL admin user/password is not valid. Please try again."))
            return False

    return _mysql_admin_check
