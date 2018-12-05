import hashlib
from flask import request, g, make_response, jsonify
from dbmodel.user_account.user_data import User
from api.apiconfig import auth, app


@app.route('/api/v1.0/users', methods=['POST'])
def create_users():
    user = User(request.form['name'], request.form['email'],
            request.form['phone'], request.form['password'], 1)
    if request.method == 'POST':
        user.add_item()
        return {'success': True}, 200, {'ContentType': 'application/json'}


@app.route('/api/v1.0/usuarios', methods=['GET', 'PUT', 'DELETE'])
@auth.login_required
def users():
    if not g.user.verificado:
        return {'success': True}, 200, {'ContentType': 'application/json'}
    if request.method == 'GET':
        return {'success': True}, 200, {'ContentType': 'application/json'}
    elif request.method == 'PUT':
        error, mssg = g.user.modify_item(
            request.form['name'], request.form['email'],
            request.form['phone'], request.form['password'])
        if error:
            return {'success': True}, 200, {'ContentType': 'application/json'}
        return {'success': True}, 200, {'ContentType': 'application/json'}
    elif request.method == 'DELETE':
        g.user.delete_item()
        return {'success': True}, 200, {'ContentType': 'application/json'}


if __name__ == '__main__':
    app.run(debug=True)
