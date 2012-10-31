Invenio Fabric
==============
Fabric library tasks for working with Invenio

Requirements:

  * Fabric 1.4+: http://docs.fabfile.org

Optional:

  * Virtualenv: http://pypi.python.org/pypi/virtualenv
  * Virtualenvwrapper: http://pypi.python.org/pypi/virtualenvwrapper
  * Pythonbrew: https://github.com/utahta/pythonbrew

Installation
============

 * Install Virtualenv, Fabric, Virutalenvwrapper, and Pythonbrew

Virtualenvwrapper:

```
export WORKON_HOME=~/envs
mkdir -p $WORKON_HOME
pip install virtualenv Fabric virtualenvwrapper invenio-fabric
curl -kL http://xrl.us/pythonbrewinstall | bash
```

Add this to your startup-file (perhaps you need to edit the path to ``virtualenvwrapper.sh``):

```
export WORKON_HOME=~/envs
source /usr/local/bin/virtualenvwrapper.sh
[[ -s $HOME/.pythonbrew/etc/bashrc ]] && source $HOME/.pythonbrew/etc/bashrc
```

To install e.g Python 2.4.6 run:

```
pythonbrew install 2.4.6
```

Usage
=====
Invenio Fabric is only a library of Fabric tasks, so you need to create your
own ``fabfile.py``. For a complete example for Atlantis Institute of Fictive Science
please see ``examples/atlantis/``. First, make sure your Invenio source code is in 
`~/src/` or alternative specify ``CFG_SRCDIR``  in your startup file:

```
export CFG_SRCDIR=~/private/src/
```

Next run:

```
cd invenio-fabric/examples/atlantis
fab -f fabfile_minimal.py loc bootstrap
fab -f fabfile_advanced.py loc:py=2.7,ref=master bootstrap
```
