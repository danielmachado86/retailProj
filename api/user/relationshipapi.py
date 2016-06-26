from flask import request, g, make_response, jsonify
from api.apiconfig import app
from dbmodel.user.usermodel import Relationship
from api.apiconfig import auth


def relationship_list(item_list):
    final_list = []
    if isinstance(item_list, Relationship):
        item = item_list
        final_list.append(item.serialize)
        return final_list
    for item in item_list:
        final_list.append(item.serialize)
    return final_list


def final_response(status_code, final_list):
    return make_response(jsonify(relaciones=final_list), status_code)


def error_response(status_code, rs):
    rs['status'] = status_code
    return make_response(jsonify(errores=rs), status_code)


@app.route('/api/v1.0/relaciones', methods=['POST', 'GET'])
@auth.login_required
def relationships():
    if not g.user.verificado:
        return error_response(403, {'message': 'Su cuenta no ha sido verificada',
                                    'action': 'Ingrese a su correo y siga las instrucciones'})
    resource = Relationship()
    if request.method == 'POST':
        error, resp = resource.add_item(
            g.user.id_usuario, request.form['amigo'])
        if error:
            return error_response(resp[0], resp[1])
        rs = final_response(resp[0], relationship_list(resource))
        rs.headers.set('Location', "/api/v1.0/relaciones/%s" % resource.id_miembro)
        return rs

    elif request.method == 'GET':
        error, item_list = resource.get_list_by_user(g.user.id_usuario)
        if error:
            resp = item_list
            return error_response(resp[0], resp[1])
        return final_response(200, relationship_list(item_list))


@app.route('/api/v1.0/relaciones/<int:item_id>', methods=['GET', 'PUT', 'DELETE'])
@auth.login_required
def relationships_item(item_id):
    if not g.user.verificado:
        return error_response(403, {'message': 'Su cuenta no ha sido verificada',
                                    'action': 'Ingrese a su correo y siga las instrucciones'})
    error, item = Relationship().get_item(item_id)
    if error:
        resp = item
        return error_response(resp[0], resp[1])
    if item.id_usuario is not g.user.id_usuario and item.id_usuario_amigo is not g.user.id_usuario:
        return error_response(403, {'message': 'No cuenta con los permisos acceder a este recurso',
                                    'action': 'Realice otra consulta'})
    if request.method == 'GET':
        return final_response(200, relationship_list(item))

    elif request.method == 'PUT':
        error, mssg = item.modify_item(request.form['status'])
        if error:
            return error_response(mssg[0], mssg[1])
        return final_response(200, relationship_list(item))

    elif request.method == 'DELETE':
        error, mssg = item.delete_item()
        if error:
            return error_response(mssg[0], mssg[1])
        return final_response(200, relationship_list(item))


if __name__ == '__main__':
    app.run(debug=True)
