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
Fabric tasks for bootstrapping, installing, deploying and running Invenio at 
CERN on Scientific Linux 5/6 hosts.

The tasks follows the guidelines on installing Invenio on SLC5/6 - see more on:

  * http://invenio-software.org/wiki/Installation/InvenioOnSLC5

Example usage:

  fab -u <user> openaire_dev bootstrap
  fab -u <user> openaire_dev install
  fab -u <user> openaire_dev deploy
  fab -u <user> openaire_dev invenio_updateconf
  
Requirements:
  * User must have sudo rights to remote machine.
  * Configuration files must be stored locally (see path for each env definiton)
  * Fabric 1.4+
"""