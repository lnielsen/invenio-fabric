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

from fabric.api import roles, cd, run, sudo, abort, env, put, task, hide
from fabric.contrib.files import comment, sed, exists
from inveniofab.env import env_settings
from inveniofab.utils import slc_version
import os

# ============================
# Invenio library tasks (SLC5)
# ============================
@roles('web')
@task
def invenio_install():
    """
    Install Invenio.
    """
    if not exists("/tmp/invenio"):
        with cd("/tmp"):
            run("git clone http://invenio-software.org/repo/invenio")

    with cd("/tmp/invenio"):
        run("aclocal && automake -a && autoconf")
        run("./configure && make")
        sudo("make install", user = "apache")
        sudo("make install-mathjax-plugin", user = "apache")
        sudo("make install-ckeditor-plugin", user = "apache")
        sudo("make install-pdfa-helper-files", user = "apache")
        sudo("make install-jquery-plugins", user = "apache")


@roles('web')
@task
def invenio_deploy():
    """
    Deploy latest Invenio master branch
    """
    with cd("/tmp/invenio"):
        run("git pull")
        run("make -s")
        sudo("make install", user = "apache")
        sudo("/opt/invenio/bin/inveniocfg --update-all", user = "apache")


@roles('web')
@task
def invenio_clean():
    """
    Clean Invenio installation
    """
    with cd("/tmp"):
        sudo("rm -Rf /tmp/invenio")
        sudo("rm -Rf /opt/invenio")


@roles('web')
@task
def invenio_configure(host = None):
    """
    Configure Invenio
    """
    invenio_updateconf(host = host)
    sudo("/opt/invenio/bin/inveniocfg --create-tables", user = "apache")
    sudo("/opt/invenio/bin/inveniocfg --create-apache-conf", user = "apache")

    slcver = slc_version()
    if slcver and slcver[0] < 6:
        comment("/opt/invenio/etc/apache/invenio-apache-vhost.conf", 'WSGIImportScript', use_sudo = True)
        comment("/opt/invenio/etc/apache/invenio-apache-vhost-ssl.conf", 'WSGIImportScript', use_sudo = True)


@roles('web')
@task
def invenio_updateconf(host = None):
    """
    Update Invenio configuration
    """
    conffile = env_settings('invenio')['conffile'] or os.path.join(os.getcwd(), 'invenio-local.conf')
    remote_conffile = "/opt/invenio/etc/invenio-local.conf"
    if not os.path.exists(conffile):
        abort("Configuration file %s does not exists." % conffile)
    put(conffile, remote_conffile, use_sudo = True)
    sudo("chown apache:apache %s" % remote_conffile)
    sudo("chmod 644 %s" % remote_conffile)

    # Adapt configuration file if needed
    if host:
        _edit_simple_cfg_option(remote_conffile, 'CFG_SITE_URL', 'http://%s' % host, use_sudo = True)
        _edit_simple_cfg_option(remote_conffile, 'CFG_SITE_SECURE_URL', 'https://%s' % host, use_sudo = True)

    sudo("/opt/invenio/bin/inveniocfg --reset-all", user = "apache")
    sudo("/opt/invenio/bin/inveniocfg --update-all", user = "apache")


@roles('web')
@task
def invenio_reset_adminpw():
    """
    Reset Invenio admin password to default.
    """
    sudo('echo "UPDATE user SET password=AES_ENCRYPT(email,\'\') WHERE nickname=\'admin\';" | sudo -u apache /opt/invenio/bin/dbexec')


@roles('web')
@task
def invenio_fix_filelinks(from_host):
    """
    Fix issues with file links
    """
    # Get records which needs to be fixed
    data = sudo('echo "SELECT id_bibrec, value FROM bibrec_bib85x join bib85x on id_bibxxx=id WHERE tag=\'8564_u\' AND value LIKE \'http://%s/%%\' ORDER BY id_bibrec;" | sudo -u apache /opt/invenio/bin/dbexec' % from_host)
    data = data.splitlines()[1:]

    try:
        # Generate MARCXML file that can be uploaded
        with open("fixfilelinksinput.xml", "w") as marcxmlfile:
            marcxmlfile.write("""<?xml version="1.0" encoding="UTF-8"?><collection xmlns="http://www.loc.gov/MARC21/slim">""")

            records = {}
            for line in data:
                (recid, fileurl) = line.split("\t")
                if recid not in records:
                    records[recid] = []
                records[recid].append(fileurl)

            for rec, urls in records.items():
                tmp = ""
                for u in urls:
                    tmp += '<datafield tag="856" ind1="4" ind2=" "><subfield code="u">%s</subfield></datafield>' % u
                marcxmlfile.write('<record><controlfield tag="001">%s</controlfield>%s</record>' % (rec, tmp))

            marcxmlfile.write("""</collection>""")

        # Upload MARCXML file
        if exists("/opt/invenio/var/tmp/fixfilelinksinput.xml"):
            sudo("rm -f /opt/invenio/var/tmp/fixfilelinksinput.xml")
        put("fixfilelinksinput.xml", "/opt/invenio/var/tmp/fixfilelinksinput.xml", use_sudo = True)
        sudo("chown apache:apache /opt/invenio/var/tmp/fixfilelinksinput.xml")
        sudo("chmod 644 /opt/invenio/var/tmp/fixfilelinksinput.xml", user = "apache")
        sudo("/opt/invenio/bin/bibupload -d /opt/invenio/var/tmp/fixfilelinksinput.xml", user = "apache")
    finally:
        if os.path.exists("fixfilelinksinput.xml"):
            os.remove("fixfilelinksinput.xml")
    #sudo("/opt/invenio/bin/bibdocfile --fix-all --yes-i-know", user = 'apache')



def _edit_simple_cfg_option(filename, opt, value, **kwargs):
    """
    Edit an configuration variable in invenio-local.conf, replace the existing value with 
    the provided one.
    """
    sed(filename, "^(%s\s*=).+$" % opt, "\\1 = %s" % value, **kwargs)

