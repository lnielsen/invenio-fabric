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

# FIXME: Move to fabfile.py for INSPIRE?

from fabric.api import task, puts, local, env
from fabric.colors import cyan
from inveniofab.git import repo_check

@task
def inspire_dbchanges():
    """ Perform INSPIRE db changes """
    puts(cyan(">>> Updating tables from INSPIRE..." % env))

    ctx = {
        'topsrcdir': repo_check('inspire', check_path=True)
    }
    ctx.update(env)

    local("cd %(topsrcdir)s; make install-dbchanges" % ctx)

    # Look for the webcoll task id added by install-dbchanges and run it
    query_output = local('echo "select max(id) from schTASK;" | %(CFG_INVENIO_PREFIX)s/bin/dbexec' % ctx,
                        capture=True)
    task_id = query_output.split('\n')[-1]

    puts(cyan(">>> Running webcoll task %s..." % task_id))
    ctx.update({'webcoll_task_id': task_id})
    local("%(CFG_INVENIO_PREFIX)s/bin/webcoll %(webcoll_task_id)s" %
          ctx)
