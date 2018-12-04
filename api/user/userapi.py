import hashlib
from flask import request, g, make_response, jsonify
from dbmodel.user_account.user_data import User
from api.apiconfig import auth, crossdomain, conditional, gzipped, app

from werkzeug.wrappers import Response


def final_response(status_code, etag):
    response = make_response(jsonify(usuario=g.user.serialize), status_code)
    response.set_etag(etag)
    response.last_modified = g.user.modificado
    return response


def response_message(status_code, rs):
    response = make_response(jsonify(errores=rs), status_code)
    return response


@app.route('/api/v1.0/users', methods=['POST'])
@crossdomain(origin='*',
             methods='GET, PUT, POST, DELETE',
             headers='Accept, Authorization, Content-Type, Origin',
             expose_headers='Date')
def create_users():
    resource = User(request.form['name'], request.form['email'],
            request.form['phone'], request.form['password'], 1)
    if request.method == 'POST':
        resource.add_item()
        response = make_response(jsonify(usuario=resource.serialize), 200)
        response.headers.set('Location', "/api/v1.0/users")
        return response


@app.route('/api/v1.0/usuarios', methods=['GET', 'PUT', 'DELETE'])
@auth.login_required
@crossdomain(origin='*',
             methods='GET, PUT, POST, DELETE',
             headers='Accept, Authorization, Content-Type, Origin',
             expose_headers='Date')
@conditional
@gzipped
def users():
    if not g.user.verificado:
        return response_message(403, {'message': 'Su cuenta no ha sido verificada',
                                      'action': 'Ingrese a su correo y siga las instrucciones'})
    etag = hashlib.sha1(jsonify(g.user.serialize).data).hexdigest()
    if request.method == 'GET':
        return final_response(200, etag)
    elif request.method == 'PUT':
        final_response(200, etag)
        error, mssg = g.user.modify_item(
            request.form['name'], request.form['email'],
            request.form['phone'], request.form['password'])
        if error:
            return response_message(mssg[0], mssg[1])
        etag = hashlib.sha1(jsonify(g.user.serialize).data).hexdigest()
        return final_response(200, etag)
    elif request.method == 'DELETE':
        response = Response()
        del response.headers['content-type']
        response.set_etag(etag)
        error, mssg = g.user.delete_item()
        if error:
            return response_message(mssg[0], mssg[1])
        del g.user
        del response.headers['etag']
        return response_message(204, {'message': 'Usuario eliminado correctamente'})


if __name__ == '__main__':
    app.run(debug=True)
