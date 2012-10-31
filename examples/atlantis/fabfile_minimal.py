from fabric.api import task
from inveniofab.api import *

@task
def loc(activate=True, **kwargs):
    """ Local environment 
    
    Likely you need to do:
    export CFG_SRCDIR="/path/to/src"
    """
    env = env_create('loc', activate=activate, **kwargs)
    return env
