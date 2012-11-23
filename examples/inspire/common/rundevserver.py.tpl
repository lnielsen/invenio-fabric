#!{{CFG_INVENIO_PREFIX}}/bin/python
from optparse import OptionParser
from wsgiref.simple_server import make_server
from invenio.webinterface_handler_flask import create_invenio_flask_app

op = OptionParser()
op.add_option('--host', dest='host', action='store', type=str,
    help='bind to this hostname/ip', default="localhost")
op.add_option('--port', dest='port', action='store', type=int,
    help='run dev server on this port', default=4000)
op.add_option('--no_debug','--no-debug', dest='no_debug', action='store_true',
    help='do not enable debug mode (reloading, exception debugger) in the app', default=False)
opts, args = op.parse_args()

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

debug = opts.no_debug == False
_app.run(debug=debug, host=opts.host, port=opts.port)
