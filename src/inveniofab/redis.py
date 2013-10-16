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

from fabric.api import task, roles
from inveniofab.utils import run_local


@task
@roles('cache')
def redis_flushdb():
    redis_cli("flushdb")


def redis_cli(cmd):
    from fabric.api import env
    opts = []
    if env.get('CFG_REDIS_PASSWORD', ''):
        opts.append('-a %s' % env.get('CFG_REDIS_PASSWORD', ''))
    if env.get('CFG_REDIS_DB', ''):
        opts.append('-n %s' % env.get('CFG_REDIS_DB', ''))
    run_local("redis-cli %s %s" % (" ".join(opts), cmd))
