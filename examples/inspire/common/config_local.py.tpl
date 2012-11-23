# -*- coding: utf-8 -*-

"""
Config for invenio-devserver
"""

import os

SRC_PATH = [
    os.path.expanduser("{{CFG_INVENIO_SRCDIR}}"),
    os.path.expanduser("{{CFG_INSPIRE_SRCDIR}}"),
]

DIRS = {
    'py': 'lib/python/invenio',
    'xsl': 'etc/bibformat/format_templates',
    'bft': 'etc/bibformat/format_templates',
    'tpl': 'etc',
    'js': 'var/www/js',
    'css': 'var/www/css',
    'png': 'var/www/img',
}