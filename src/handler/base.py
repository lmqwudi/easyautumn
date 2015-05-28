# -*- coding:utf-8 -*-

import sys
import json
import functools

import tornado.gen
import tornado.web
from tornado import httputil
from tornado.log import gen_log
from tornado.web import HTTPError

from util.error import (
    ECError,
    MissingArgumentError,
    NotValidTokenError,
    NotAllowedError,
    RequestBodyError,
    NotValidCORS
)

from util import log
from util import crypt

from conf.config import AUTH_ONLINE_SWITCH
from conf.config import COOKIE_DOMAIN

AUTH_ORIGIN_LIST = [
    # '' means not a cors request
    '',
    'http://ec.kuaizhan.com',
    'ec.kuaizhan.com',
    'http://ec.t1.com',
    'ec.t1.com',
    'http://kuaizhan.com',
    'kuaizhan.com',
    'http://www.kuaizhan.com',
    'www.kuaizhan.com'
]

logger = log.LogService().getLogger()


class BaseHandler(tornado.web.RequestHandler):

    def prepare(self):
        self._trans_json_body()

    def _trans_json_body(self):
        content_type = self.request.headers.get('Content-Type', '')
        if content_type.lower().startswith('application/json'):
            try:
                body_data = json.loads(self.request.body)
                if not isinstance(body_data, dict):
                    raise RequestBodyError('JSON Body not Dictionary')
            except:
                raise RequestBodyError('Request Body not JSON')
            tornado_arg_data = {k: [self._ec_encode_argument(k, body_data[k])] for k in body_data}
            self.request.arguments.update(tornado_arg_data)

    def _ec_encode_argument(self, k, v):
        ''' All http argument must be string
        Unicode not work with transform of 'str'
        '''
        return v if isinstance(v, unicode) else str(v)

    def get_current_user(self, allow_t=False):
        return self._get_current_user(allow_t=allow_t)

    def _get_current_user(self, dynamic_token=True, allow_t=False):
        token = self.get_argument('ecinf', None)
        if token:
            token = token.replace(' ', '+')
            store_id = crypt.decrypt(token, dynamic_token)
            if store_id:
                self.set_cookie(
                    'ecinf', token, expires_days=None,
                    domain=COOKIE_DOMAIN, httponly=True)
                return store_id

        if allow_t or not AUTH_ONLINE_SWITCH:
            t_token = self.get_argument('t_token', None)
            if t_token:
                token = crypt.encrypt(t_token.encode('utf-8'))
                self.set_cookie(
                    'ecinf', token, expires_days=None,
                    domain=COOKIE_DOMAIN, httponly=True)
                return t_token

        token = self.get_cookie('ecinf', None)
        if token:
            token = token.replace(' ', '+')
            store_id = crypt.decrypt(token, dynamic_token)
            if store_id:
                self.set_cookie(
                    'ecinf', token, expires_days=None,
                    domain=COOKIE_DOMAIN, httponly=True)
                return store_id

        return None

    def set_default_headers(self):
        pass

    def options(self, *args, **kwargs):
        # Cors not simple request would check first by OPTIONS
        origin = self.request.headers.get('origin', '')
        if origin in AUTH_ORIGIN_LIST:
            self.set_header('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE')
            self.set_header('Access-Control-Allow-Headers', 'accept,content-type')
        self.finish()

    def wrap_response(self, **ret):
        #: param fields: (key, name, default)
        fields = (
            ('code', 'code', 0),
            ('msg', 'msg', ''),
            ('data', 'data', {}))
        d = {name: ret.get(k, default) for k, name, default in fields}
        return json.dumps(d)

    def gen_params(self, keys_def):
        return {x[0]: x[1]
                for x in map(lambda x: self._transform(x), keys_def)
                if x[1] is not None}

    def _transform(self, key_def):
        key, rename, default, transform, field_check, need = key_def
        # `default` is for the init input value
        # Query string as: 'a=&b=c', get_argument('a', None)
        # would get '' instead of None
        v = self.get_argument(key, '') or default

        if v is None and need:
            raise MissingArgumentError(key)

        if field_check and (v is not None):
            v = field_check(key, v)

        if transform and (v is not None):
            v = transform(v)

        if rename == '_no_mean_':
            v = None

        return rename, v

    def _handle_request_exception(self, e):
        if not isinstance(e, ECError):
            self.log_exception(*sys.exc_info())
        if self._finished:
            return
        if isinstance(e, HTTPError):
            if e.status_code not in httputil.responses and not e.reason:
                gen_log.error("Bad HTTP status code: %d", e.status_code)
                self.finish({'code': 500, 'msg': 'Internal Error'})
            else:
                self.finish({'code': e.status_code, 'msg': sys.exc_info})
        elif isinstance(e, ECError):
            logger.error('Ec error: %d, %s', e.status_code, e.msg)
            self.finish({'code': e.status_code, 'msg': e.msg})
        else:
            self.finish({'code': 500, 'msg': 'Internal Error'})

    def gen_cookie_str(self):
        cookies = ';'.join(
            '{0}={1}'.format(name, cookie.value)
            for name, cookie
            in self.request.cookies.iteritems())
        return cookies

    def _verify_sign(self, arg_names=None):
        reserved_keys = ['appid']
        arg_names = arg_names or []
        arg_names.extend(reserved_keys)

        e_so_sig = self.get_argument('so_sig', '')
        args = {k: self.get_argument(k, '') for k in arg_names}
        so_sig = crypt.sign(**args)
        logger.debug('sign, transfer - %s, computed - %s', e_so_sig, so_sig)
        return so_sig == e_so_sig

def auth(must_in_store=True):
    def wrapper(method):
        @functools.wraps(method)
        def _(handler, *args, **kwargs):
            store_id_cookie = handler.get_current_user()
            if store_id_cookie is None:
                raise NotValidTokenError()
            elif must_in_store and 'store_id' in kwargs:
                # Current user has AUTH of current store
                # whick means: store_id_in_cookie == store_id
                if store_id_cookie != kwargs['store_id']:
                    logger.error(
                        'Ec error: cookie store_id - %s, store_id - %s',
                        store_id_cookie, kwargs['store_id'])
                    raise NotAllowedError()
            return method(handler, *args, **kwargs)
        return _
    return wrapper


def cors(allow=True, simple=True, with_credentials=False):
    def wrapper(method):
        @functools.wraps(method)
        def _(handler, *args, **kwargs):
            need_check_origin = False
            '''
                For POST, there may be csrf problems,
                Server side may handle it as same-orgin request,
                So, must be decorated with cors in default to check the origin

                So, there is 4 types of request:
                    1. simple cors
                    2. cors but not simple
                    3. post not cors(may have problems)
                    4. not cors: get, put, ...
            '''
            if not allow:
                '''
                Decorate `post() with cors(allow=False)`, to make
                it the strict cors request, thus prevent csrf prolem
                '''
                need_check_origin = True
            elif with_credentials:
                need_check_origin = True
                handler.set_header('Access-Control-Allow-Credentials', 'true')
            elif simple:
                handler.set_header('Access-Control-Allow-Origin', '*')
            else:
                need_check_origin = True
            if need_check_origin:
                origin = handler.request.headers.get('origin', '')
                if origin in AUTH_ORIGIN_LIST:
                    handler.set_header('Access-Control-Allow-Origin', origin)
                else:
                    logger.warn('Not allowed cors request, Origin: %s', origin)
                    # Terminate the request process to prevent side effect
                    raise NotValidCORS()
            return method(handler, *args, **kwargs)
        return _
    return wrapper


