Invenio Fabric
==============

Fabric library tasks for working with Invenio

Requirements
------------

 * Install Virtualenv

Run ``pip install virtualenv`` or install via your favourite package manager (e.g. ``sudo aptitude install python-virtualenv``).

 * Install Virtualenvwrapper::

    pip install virtualenvwrapper
    export WORKON_HOME=~/envs
    mkdir -p $WORKON_HOME
    source /usr/local/bin/virtualenvwrapper.sh

Add line 2 and 4 to your shell startup file. Also note that depending on your system ``virtualenvwrapper.sh`` might be installed at a different location than /usr/local/bin. For more elaborate documentation, see http://virtualenvwrapper.readthedocs.org/en/latest/install.html

 * Install Pythonbrew (optional)

Pythonbrew is optional, but it allows your to install several different python versions without messing up your system Python. To install Pythonbrew run::

    curl -kL http://xrl.us/pythonbrewinstall | bash

and add following to your shell startup file::

    [[ -s $HOME/.pythonbrew/etc/bashrc ]] && source $HOME/.pythonbrew/etc/bashrc

For more elaborate installation instructions please see https://github.com/utahta/pythonbrew. You should now be able to run e.g. ``pythonbrew list`` or to install Python 2.4.6 run ``pythonbrew install 2.4.6``.

Installation
------------
Create a new virtualenv (optional)::

    mkvirtualenv fabenv
    workon fabenv

Then install invenio-fabric via PyPI::

    pip install invenio-fabric
    export CFG_SRCDIR=~/private/src


Add the last line to your shell startup file.

*Important:* ``CFG_SRCDIR`` should not point to your Invenio source directory, but to one level above. Also, your Invenio source code directory should be named ``invenio``. See directory layout below.::

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

Note, you do not need to specify ``CFG_SRCDIR``, in which case the Fabric task will checkout a fresh copy from the GIT repository.

Usage documentation
-------------------


API documentation
-----------------

.. toctree::
   :maxdepth: 1
   :glob:

   api/*

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

