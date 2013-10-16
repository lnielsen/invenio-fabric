#!{{CFG_INVENIO_PREFIX}}/bin/python
from invenio.webinterface_handler_flask import create_invenio_flask_app

_app = create_invenio_flask_app()

_app.run(port={{CFG_INVENIO_PORT_HTTP}})
