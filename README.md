Invenio Fabric
==============
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