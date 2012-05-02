Invenio Fabric
==============
Fabric tasks for bootstrapping, installing, deploying and running Invenio on CERN Scientific 
Linux 5/6 hosts.

The tasks follows the guidelines on installing Invenio on SLC5/6 - see more on:

  * http://invenio-software.org/wiki/Installation/InvenioOnSLC5

Requirements:

  * User must have sudo rights to remote machine.
  * Configuration files must be stored locally (see path for each env definiton)
  * Fabric 1.4+
  
Example usage::

  fab -u <user> openaire_dev bootstrap
  fab -u <user> openaire_dev install
  fab -u <user> openaire_dev deploy
  fab -u <user> openaire_dev invenio_updateconf