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
Fabric tasks for bootstrapping, installing, deploying and running Atlantis.

Examples
--------
Setup virtual environment and database with Python 2.4 and Invenio v1.1.0:
  fab loc:py=24,ref=origin/v1.1.0 bootstrap
  fab loc:py=24,ref=origin/v1.1.0 invenio_create_demosite

Dump, load and drop (database and virtual environment):
  fab loc:py=27,ref=master dump
  fab loc:py=27,ref=master load
  fab loc:py=27,ref=master drop

Requirements:
 * pythonbrew must be installed to specify a specific Python version.
"""

from fabric.api import task, abort
from fabric.colors import red
from inveniofab.api import *
import os

@task
def loc(activate=True, py=None, ref=None, **kwargs):
    """
    Local environment (example: loc:py=24,ref=maint-1.1)
    """
    if 'name' not in kwargs:
        kwargs['name'] = env_make_name('atlantis', py or '', ref or '')

    env = env_create('loc', activate=activate, python=py, **kwargs)

    return env_override(env, 'invenio', ref)
