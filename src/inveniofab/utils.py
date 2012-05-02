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

from fabric.api import env, run
import re

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