#!{{CFG_INVENIO_PREFIX}}/bin/python
from wsgiref.simple_server import make_server
from invenio.webinterface_handler_flask import create_invenio_flask_app

_app = create_invenio_flask_app()

@_app.route('/css/<path:filename>')
def download_file(filename):
    return _app.send_static_file('css/'+filename)

@_app.route('/img/<path:filename>')
def download_file_img(filename):
    return _app.send_static_file('img/'+filename)

@_app.route('/js/<path:filename>')
def download_file_js(filename):
    return _app.send_static_file('js/'+filename)

global CFG_WSGI_SERVE_STATIC_FILES
CFG_WSGI_SERVE_STATIC_FILES = True

_app.run(debug=True, port={{CFG_INVENIO_PORT_HTTPS}})
