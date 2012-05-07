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
Fabric library tasks for bootstrapping, installing, deploying, running and copying Invenio at 
CERN on Scientific Linux 5/6 hosts.

The tasks follows the guidelines on installing Invenio on SLC5/6 - see more on:

  * http://invenio-software.org/wiki/Installation/InvenioOnSLC5

Requirements:

  * User must have sudo rights to remote machine.
  * Configuration files must be stored locally (see path for each env definiton)
  * Fabric 1.4+

Usage
=====
Invenio Fabric is only a library of Fabric tasks, so you need to create your
own ``fabfile.py``. For a complete example for Atlantis Institute of Fictive Science
please see ``examples/atlantis/``. A basic fabfile would allow your to run commands like: 

  * ``fab -u <user> env_atlantis:<hostname> bootstrap``
  * ``fab -u <user> env_atlantis:<hostname> install``
  * ``fab -u <user> env_atlantis:<hostname> deploy``
  * ``fab -u <user> env_atlantis:<hostname> invenio_updateconf``
  
Usually your fabfile for your Invenio installation would need only to define tasks for 
defining your environments (e.g. production, integration, testing).
"""