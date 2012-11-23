Invenio Fabric
==============
Fabric library tasks for working with Invenio

Requirements:

  * Fabric 1.4+: http://docs.fabfile.org
  * Virtualenv: http://pypi.python.org/pypi/virtualenv
  * Virtualenvwrapper: http://pypi.python.org/pypi/virtualenvwrapper

Optional:

  * Pythonbrew: https://github.com/utahta/pythonbrew

*Important:* Invenio Fabric requires you to already have system dependencies installed (e.g. OpenOffice etc). Please see http://invenio-software.org/wiki/Installation or e.g. https://github.com/lnielsen-cern/invenio-vagrant/blob/master/provision-ubuntu.sh for how to install system dependencies on your system.

*Python 2.4:* If you are planning to use Pythonbrew with Python 2.4, you must install virtualenv 1.7.2 (or lower), as virtualenv 1.8 dropped support for Python 2.4.

Requirements
============

 * Install Virtualenv

Run ``pip install virtualenv`` or install via your favourite package manager (e.g. ``sudo aptitude install python-virtualenv``).

 * Install Virtualenvwrapper

```
pip install virtualenvwrapper
export WORKON_HOME=~/envs
mkdir -p $WORKON_HOME
source /usr/local/bin/virtualenvwrapper.sh
```

Add line 2 and 4 to your shell startup file. Also note that depending on your system ``virtualenvwrapper.sh`` might be installed at a different location than /usr/local/bin. For more elaborate documentation, see http://virtualenvwrapper.readthedocs.org/en/latest/install.html

 * Install Pythonbrew (optional)

Pythonbrew is optional, but it allows your to install several different python versions without messing up your system Python. To install Pythonbrew run:

```
curl -kL http://xrl.us/pythonbrewinstall | bash
```

and add following to your shell startup file.

```
[[ -s $HOME/.pythonbrew/etc/bashrc ]] && source $HOME/.pythonbrew/etc/bashrc
```

For more elaborate installation instructions please see https://github.com/utahta/pythonbrew. You should now be able to run e.g. ``pythonbrew list`` or to install Python 2.4.6 run ``pythonbrew install 2.4.6``.

Installation
============

Create a new virtualenv (optional):

```
mkvirtualenv fabenv
workon fabenv
```

Then install invenio-fabric via PyPI:

```
pip install invenio-fabric
export CFG_SRCDIR=~/private/src
```

Add the last line to your shell startup file.

*Important:* ``CFG_SRCDIR`` should not point to your Invenio source directory, but to one level above. Also, your Invenio source code directory should be named ``invenio``. See directory layout below.

```
$ export CFG_SRCDIR=~/src
$ cd CFG_SRCDIR
$ ls -1
invenio
$ cd CFG_SRCDIR/invenio/
$ ls -1
ABOUT-NLS
aclocal.m4
AUTHORS
autom4te.cache
ChangeLog
config
config.guess
...
```

Note, you do not need to specify ``CFG_SRCDIR``, in which case the Fabric task will checkout a fresh copy from the GIT repository.

Usage example
=============

To install Invenio master branch
```
workon fabenv
cdvirtualenv
cd share/atlantis/
fab loc bootstrap
fab loc invenio_create_demosite
workon atlantis
cdvirtualenv
serve
```

or alternatively to bootstrap Invenio next:

```
fab loc:py=27,ref=next bootstrap
fab loc:py=27,ref=next devserver_install_flask
workon atlantis27next
rundevserver.py
```

fabfile.py
==========
Invenio Fabric is only a library of Fabric tasks, so for most projects you need to create your
own ``fabfile.py``. For a complete example for Atlantis Institute of Fictive Science
please see ``examples/atlantis/``.

Following is an example of basic ``fabfile.py`` for Atlantis.

```
from fabric.api import task
from inveniofab.api import *
import os

@task
def loc(activate=True, py=None, ref=None, **kwargs):
    """ Local environment (example: loc:py=24,ref=maint-1.1) """
    if 'name' not in kwargs:
        kwargs['name'] = env_make_name('atlantis', py or '', ref or '')
    env = env_create('loc', activate=activate, python=py, **kwargs)
    return env_override(env, 'invenio', ref)
```

With that you have the following commands available:
```
    apache_restart           Restart Apache
    apache_start             Restart Apache
    apache_stop              Restart Apache
    bootstrap                Bootstrap Invenio installation
    devserver_conf           Upload and update Invenio configuration
    devserver_install_flask  Install a Flask devserver
    drop                     Remove installation
    dump                     Archive installation
    install                  Install changes
    invenio_conf             Upload and update Invenio configuration
    invenio_create_demosite  Create Invenio demo site
    invenio_createdb         Create Invenio tables
    invenio_upgrade          Upgrade Invenio
    load                     Load archived installation
    loc                      Local environment (example: loc:py=24,ref=maint-1.1)
    mysql_copy               Copy database from latest available dump.
    mysql_createdb           Create database and user
    mysql_dropdb             Drop database and user
    mysql_dump               Dump database to file
    mysql_load               Load MySQL dump file
    repo_configure           Configure repository
    repo_install             Run configure and make
    repo_make                Run make in repository
    repo_prepare             Prepare source code after fresh checkout
    repo_setup               Clone repository
    repo_update              Pull repository updates
    test_clean               Clean Invenio logs and temporary files
    test_dump                Dump a test environment
    test_load                Load test environment
    test_reset_admin         Reset admin password
    venv_create              Create virtualenv environment
    venv_drop                Drop virtualenv environment
    venv_dump                Archive a virtualenv
    venv_load                Load an archived virtualenv
    venv_pyuno_install       Install Python OpenOffice binding
    venv_requirements        Install Python requirements
```

Command Reference
=================
Many commands takes some parameters. For now, please look in the source code, until I get time to document them.
