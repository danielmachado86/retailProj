import hashlib

from flask import Flask, g, jsonify, render_template, request, current_app, abort, after_this_request
from dbmodel.user_account.user_data import User, verify_auth_token, get_user_by_id, get_user_by_mail
from flask_httpauth import HTTPBasicAuth

import json
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
from flask import make_response
import requests

from datetime import timedelta, datetime
from functools import update_wrapper
from werkzeug import exceptions
import io
import gzip
import functools

from logging.config import dictConfig

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'formatter': 'default'
    }},
    'root': {
        'level': 'DEBUG',
        'handlers': ['wsgi']
    }
})


from werkzeug.wrappers import ETagResponseMixin, Response

app = Flask(__name__)
auth = HTTPBasicAuth()

CLIENT_ID = json.loads(
    open('././res/google_client_secrets.json', 'r').read())['web']['client_id']


def make_list(item_list, obj):
    final_list = []
    if isinstance(item_list, obj):
        item = item_list
        final_list.append(item.serialize)
        return final_list
    for item in item_list:
        final_list.append(item.serialize)
    return final_list


def final_response(final_list, status_code):
    json_data = jsonify(final_list)
    etag = hashlib.sha1(json_data.data).hexdigest()
    response = make_response(json_data, status_code)
    response.set_etag(etag)
    response.last_modified = g.user.modificado
    return response


def response_message(status_code, rs):
    rs['status'] = status_code
    return make_response(jsonify(errores=rs), status_code)


def check_account_verification():
    return response_message(403, {'message': 'Su cuenta no ha sido verificada',
                                  'action': 'Ingrese a su correo y siga las instrucciones'})


@auth.verify_password
def verify_password(username_or_token, password):
    user_id = verify_auth_token(username_or_token)
    if user_id:
        user = get_user_by_id(user_id)
    else:
        user = get_user_by_mail(username_or_token)
        if not user or not user.verify_password(password):
            return False
    g.user = user
    return True


@app.route('/api/v1.0/token')
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token()
    return jsonify({'token': token.decode('ascii')})


@app.route('/api/v1.0/clientOAuth')
def start():
    return render_template('clientOAuth.html')


@app.route('/api/v1.0/oauth/<provider>', methods=['POST'])
def login(provider):
    # STEP 1 - Parse the auth code
    auth_code = request.json.get('auth_code')
    print("Step 1 - Complete, received auth code %s" % auth_code)
    if provider == 'google':
        # STEP 2 - Exchange for a token
        try:
            # Upgrade the authorization code into a credentials object
            oauth_flow = flow_from_clientsecrets('../../res/google_client_secrets.json', scope='')
            oauth_flow.redirect_uri = 'postmessage'
            credentials = oauth_flow.step2_exchange(auth_code)
        except FlowExchangeError:
            response = make_response(json.dumps('Failed to upgrade the authorization code.'), 401)
            response.headers['Content-Type'] = 'application/json'
            return response

        # Check that the access token is valid.
        access_token = credentials.access_token
        url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' % access_token)
        h = httplib2.Http()
        result = json.loads(h.request(url, 'GET')[1].decode())
        # If there was an error in the access token info, abort.
        if result.get('error') is not None:
            response = make_response(json.dumps(result.get('error')), 500)
            response.headers['Content-Type'] = 'application/json'

        # # Verify that the access token is used for the intended user_account.
        # gplus_id = credentials.id_token['sub']
        # if result['user_id'] != gplus_id:
        #     response = make_response(json.dumps("Token's user_account ID doesn't match given user_account ID."), 401)
        #     response.headers['Content-Type'] = 'application/json'
        #     return response

        # # Verify that the access token is valid for this app.
        # if result['issued_to'] != CLIENT_ID:
        #     response = make_response(json.dumps("Token's client ID does not match app's."), 401)
        #     response.headers['Content-Type'] = 'application/json'
        #     return response

        # stored_credentials = login_session.get('credentials')
        # stored_gplus_id = login_session.get('gplus_id')
        # if stored_credentials is not None and gplus_id == stored_gplus_id:
        #     response = make_response(json.dumps('Current user_account is already connected.'), 200)
        #     response.headers['Content-Type'] = 'application/json'
        #     return response
        print("Step 2 Complete! Access Token : %s " % credentials.access_token)

        # STEP 3 - Find User or make a new one

        # Get user_account info
        h = httplib2.Http()
        userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
        params = {'access_token': credentials.access_token, 'alt': 'json'}
        answer = requests.get(userinfo_url, params=params)

        data = answer.json()

        print(data)

        name = data['name']
        picture = data['picture']
        email = data['email']
        verified = data['verified_email']

        # see if user_account exists, if it doesn't make a new one

        user = User().get_item_by_mail(email, 2)
        if not user:
            user = User()
            user.add_item(name, email, None, None, picture, 2)
            if verified is True:
                user.verify_account()

        # STEP 4 - Make token
        token = user.generate_auth_token(600)

        # STEP 5 - Send back token to the client
        return jsonify({'token': token.decode('ascii')})

        # return jsonify({'token': token.decode('ascii'), 'duration': 600})
    else:
        return 'Unrecoginized Provider'


class NotModified(exceptions.HTTPException):
    code = 304

    def get_response(self, *kwargs):
        response = Response(status=304)
        max_age = 60
        response.cache_control.max_age = max_age
        response.cache_control.private = True
        response.date = datetime.utcnow()
        response.expires = response.date + timedelta(0, max_age)
        return response


class PreconditionRequired(exceptions.HTTPException):
    code = 428
    description = ('<p>This request is required to be '
                   'conditional; try using "If-Match".')
    name = 'Precondition Required'

    def get_response(self, environment):
        resp = super(PreconditionRequired,
                     self).get_response(environment)
        resp.status = str(self.code) + ' ' + self.name.upper()
        return resp


def conditional(func):
    '''Start conditional method execution for this resource'''

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        g.condtnl_etags_start = True
        return func(*args, **kwargs)

    return wrapper


_old_set_etag = ETagResponseMixin.set_etag


@functools.wraps(ETagResponseMixin.set_etag)
def _new_set_etag(self, etag, weak=False):
    # only check the first time through; when called twice
    # we're modifying
    if (hasattr(g, 'condtnl_etags_start') and
            g.condtnl_etags_start):
        if request.method in ('PUT', 'DELETE', 'PATCH'):
            if not request.if_match:
                raise PreconditionRequired
            if etag not in request.if_match:
                abort(412)
        elif (request.method == 'GET' and
                  request.if_none_match and
                      etag in request.if_none_match):
            raise NotModified
        g.condtnl_etags_start = False
    _old_set_etag(self, etag, weak)


ETagResponseMixin.set_etag = _new_set_etag


def crossdomain(origin=None, methods=None, headers=None, expose_headers=None,
                max_age=21600, attach_to_all=True,
                automatic_options=True, credentials=False):
    if methods is not None and not isinstance(methods, str):
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, str):
        headers = ', '.join(x.upper() for x in headers)
    if expose_headers is not None and not isinstance(expose_headers, str):
        expose_headers = ', '.join(x.upper() for x in expose_headers)
    if not isinstance(origin, str):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers

            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            if credentials:
                h['Access-Control-Allow-Credentials'] = 'true'
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            if expose_headers is not None:
                h['Access-Control-Expose-Headers'] = expose_headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)

    return decorator


def gzipped(f):
    @functools.wraps(f)
    def view_func(*args, **kwargs):
        @after_this_request
        def zipper(response):
            accept_encoding = request.headers.get('Accept-Encoding', '')

            if 'gzip' not in accept_encoding.lower():
                return response

            response.direct_passthrough = False

            if (response.status_code < 200 or
                        response.status_code >= 300 or
                        'Content-Encoding' in response.headers):
                return response
            gzip_buffer = io.BytesIO()
            gzip_file = gzip.GzipFile(mode='wb',
                                      fileobj=gzip_buffer)
            gzip_file.write(response.data)
            gzip_file.close()

            response.data = gzip_buffer.getvalue()
            response.headers['Content-Encoding'] = 'gzip'
            response.headers['Vary'] = 'Accept-Encoding'
            response.headers['Content-Length'] = len(response.data)

            return response

        return f(*args, **kwargs)

    return view_func


@app.after_request
def add_header(response):
    max_age = 60
    response.cache_control.max_age = max_age
    response.cache_control.private = True
    response.date = datetime.utcnow()
    response.expires = response.date + timedelta(0, max_age)
    return response
