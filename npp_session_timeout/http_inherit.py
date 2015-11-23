# __author__ = 'truongdung'

import openerp
import time
import os
import logging
from openerp.http import Root, JsonRequest, SessionExpiredException, AuthenticationError
from openerp import http

_logger = logging.getLogger(__name__)

SESSION_TIMEOUT = 30 * 60 * 60 and openerp.tools.config['session_timeout']


def session_gc(session_store):
    last_week = time.time() - int(SESSION_TIMEOUT)
    for f_name in os.listdir(session_store.path):
        path = os.path.join(session_store.path, f_name)
        try:
            if os.path.getmtime(path) < last_week:
                os.unlink(path)
        except OSError:
            pass


def setup_session(self, http_request):
    # recover or create session
    session_gc(self.session_store)

    sid = http_request.args.get('session_id')
    explicit_session = True
    if not sid:
        sid = http_request.headers.get("X-Openerp-Session-Id")
    if not sid:
        sid = http_request.cookies.get('session_id')
        explicit_session = False
    if sid is None:
        http_request.session = self.session_store.new()
    else:
        http_request.session = self.session_store.get(sid)
    return explicit_session


def _handle_exception(self, exception):
    """Called within an except block to allow converting exceptions
        to arbitrary responses. Anything returned (except None) will
        be used as response."""
    try:
        return eval('super(JsonRequest, self)._handle_exception(exception)')
    except eval('Exception'):
        if not isinstance(exception, (openerp.exceptions.Warning, SessionExpiredException)):
            _logger.exception("Exception during JSON request handling.")
        error = {
            'code': 200,
            'message': "Odoo Server Error",
            'data': http.serialize_exception(exception)
        }
        if isinstance(exception, AuthenticationError):
            error['code'] = 100
            error['message'] = "Odoo Session Invalid"
        if isinstance(exception, SessionExpiredException):
            error['code'] = 100
            error['message'] = "Odoo Session Expired"
        if exception.name == 'Not Found' and exception.code == 404:
            error['code'] = 100
            error['message'] = "Odoo Session Expired"
            error['data']['name'] = 'werkzeug.exceptions.Forbidden'
        return self._json_response(error=error)

Root.setup_session = setup_session
JsonRequest._handle_exception = _handle_exception