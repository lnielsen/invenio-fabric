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
Fabric library tasks for bootstrapping, installing, running and copying Invenio

Usage
=====
Invenio Fabric is only a library of Fabric tasks, so you need to create your
own ``fabfile.py``. For a complete example for Atlantis Institute of Fictive 
Science please see ``examples/atlantis/``. A basic fabfile would allow your to 
run commands like: 

  * ``fab loc bootstrap``
  
Usually your fabfile for your Invenio installation would need only to define 
tasks for defining your environments (e.g. production, integration, testing).
"""