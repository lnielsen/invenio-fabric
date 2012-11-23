{% if WITH_DEVSCRIPTS %}
export PYVER=`{{PYTHON}} -c "import sys;print '%s.%s' % (sys.version_info[0],sys.version_info[1])"`
export CFG_INVENIO_SRCDIR={{CFG_INVENIO_SRCDIR}}
export CFG_INVENIO_PREFIX={{CFG_INVENIO_PREFIX}}
export CFG_INVENIO_USER={{CFG_INVENIO_USER}}
export CFG_INVENIO_HOSTNAME={{CFG_INVENIO_HOSTNAME}}
export CFG_INVENIO_DOMAIN={{CFG_INVENIO_DOMAIN}}
export CFG_INVENIO_PORT_HTTP={{CFG_INVENIO_PORT_HTTP}}
export CFG_INVENIO_PORT_HTTPS={{CFG_INVENIO_PORT_HTTPS}}
alias mi="{{CFG_INVENIO_PREFIX}}/bin/invenio-make-install"
alias kw="{{CFG_INVENIO_PREFIX}}/bin/invenio-check-kwalitee --check-some"
{% endif %}
if [ -e {{CFG_INVENIO_PREFIX}}/etc/bash_completion.d/inveniocfg ];
then
    . {{CFG_INVENIO_PREFIX}}/etc/bash_completion.d/inveniocfg
fi