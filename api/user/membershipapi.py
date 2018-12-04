# from flask import request, g
# from api.apiconfig import (auth, crossdomain, conditional, gzipped, app, check_account_verification,
#                            response_message, final_response, make_list)
#
# from dbmodel.user_account.group_data import Group, Membership
#
# collection_name = 'grupos'
#
#
# @app.route('/v1.0/me/groups', methods=['POST', 'GET'])
# @auth.login_required
# @crossdomain(origin='*',
#              methods='GET, PUT, POST, DELETE',
#              headers='Accept, Authorization, Content-Type, Origin',
#              expose_headers='Date')
# @conditional
# @gzipped
# def me_group():
#     if not g.user_account.verificado:
#         return check_account_verification()
#     if request.method == 'POST':
#         resource = Group()
#         error, resp = resource.add_item(
#             g.user_account.id_usuario, request.form['group_type'], request.form['group_name'], request.form['description'])
#         if error:
#             return response_message(resp[0], resp[1])
#         rs = final_response(
#             {collection_name: make_list(resource, Group)}, resp[0])
#         rs.headers.set('Location', "/v1.0/groups/{}".format(resource.id_grupo))
#         return rs
#     elif request.method == 'GET':
#         resource = Membership()
#         error, item_list = resource.get_list_by_user(g.user_account.id_usuario, g.user_account.id_usuario)
#         if error:
#             resp = item_list
#             return response_message(resp[0], resp[1])
#         return final_response(
#             {collection_name: make_list(item_list, Membership)}, 200)
#
#
# @app.route('/v1.0/groups', methods=['POST', 'GET'])
# @auth.login_required
# @crossdomain(origin='*',
#              methods='GET, PUT, POST, DELETE',
#              headers='Accept, Authorization, Content-Type, Origin',
#              expose_headers='Date')
# @conditional
# @gzipped
# def groups():
#     if not g.user_account.verificado:
#         return check_account_verification()
#     elif request.method == 'GET':
#         resource = Group()
#         error, item_list = resource.get_list()
#         if error:
#             resp = item_list
#             return response_message(resp[0], resp[1])
#         return final_response(
#             {collection_name: make_list(item_list, Group)}, 200)
#
#
# @app.route('/v1.0/groups/<int:item_id>', methods=['GET', 'PUT', 'DELETE'])
# @auth.login_required
# @crossdomain(origin='*',
#              methods='GET, PUT, POST, DELETE',
#              headers='Accept, Authorization, Content-Type, Origin',
#              expose_headers='Date')
# @conditional
# @gzipped
# def group_item(item_id):
#     if not g.user_account.verificado:
#         return check_account_verification()
#     error, item = Group().get_item(item_id)
#     if error:
#         resp = item
#         return response_message(resp[0], resp[1])
#     if request.method == 'GET':
#         return final_response(
#             {collection_name: item.serialize}, 200)
#     elif request.method == 'PUT':
#         final_response(
#             make_list(item, Group), 200)
#         error, mssg = item.modify_item(request.form['group_type'],
#                                        request.form['group_name'],
#                                        request.form['description'],
#                                        g.user_account.id_usuario)
#         if error:
#             return response_message(mssg[0], mssg[1])
#         return final_response(
#             {collection_name: item.serialize}, 200)
#     elif request.method == 'DELETE':
#         error, mssg = item.delete_item(g.user_account.id_usuario)
#         return response_message(mssg[0], mssg[1])
#
#
# @app.route('/v1.0/groups/<int:group_id>/users', methods=['POST', 'GET'])
# @auth.login_required
# @crossdomain(origin='*',
#              methods='GET, PUT, POST, DELETE',
#              headers='Accept, Authorization, Content-Type, Origin',
#              expose_headers='Date')
# @conditional
# @gzipped
# def membership(group_id):
#     if not g.user_account.verificado:
#         return check_account_verification()
#     resource = Membership()
#     if request.method == 'POST':
#         error, resp = resource.add_item(
#             g.user_account.id_usuario, group_id, 3, None)
#         if error:
#             return response_message(resp[0], resp[1])
#         rs = final_response(
#             {'usuarios': make_list(resource.grupo, Group)}, resp[0])
#         rs.headers.set('Location', "/v1.0/grupos/{}".format(group_id))
#         return rs
#
#     elif request.method == 'GET':
#         error, item_list = resource.get_list_by_group(group_id, g.user_account.id_usuario)
#         if error:
#             resp = item_list
#             return response_message(resp[0], resp[1])
#         return final_response(
#             {'usuarios': make_list(item_list, Membership)}, 200)
#
#
# @app.route('/v1.0/groups/<int:group_id>/users/<int:user_id>', methods=['POST', 'PUT'])
# @auth.login_required
# @crossdomain(origin='*',
#              methods='GET, PUT, POST, DELETE',
#              headers='Accept, Authorization, Content-Type, Origin',
#              expose_headers='Date')
# # @conditional
# @gzipped
# def membership_request(user_id, group_id):
#     if not g.user_account.verificado:
#         return check_account_verification()
#     if request.method == 'POST':
#         resource = Membership()
#         if 'role' not in request.form or 'updated_by' not in request.form:
#             return response_message(400, {'message': 'No suministró parámetros validos',
#                                           'action': 'Realice una nueva solicitud incluyendo role y updated_by'})
#         error, resp = resource.add_item(
#             user_id, group_id, request.form['role'], request.form['updated_by'])
#         if error:
#             return response_message(resp[0], resp[1])
#         rs = final_response(
#             {'usuarios': resource.serialize}, resp[0])
#         rs.headers.set('Location', "/v1.0/grupos/{}".format(group_id))
#         return rs
#
#     elif request.method == 'PUT':
#         error, item = Membership().get_item(group_id, user_id)
#         if error:
#             resp = item
#             return response_message(resp[0], resp[1])
#         final_response(
#             {'usuarios': item.serialize}, 200)
#         if 'status' in request.form:
#             error, mssg = item.new_status(request.form['status'], g.user_account.id_usuario)
#             if error:
#                 return response_message(mssg[0], mssg[1])
#             return final_response(
#                 {'usuarios': item.serialize}, 200)
#         if 'role' in request.form:
#             error, resp = item.role_change(request.form['role'], g.user_account.id_usuario)
#             if error:
#                 return response_message(resp[0], resp[1])
#             return final_response(
#                 {'usuarios': item.serialize}, 200)
#         return response_message(400, {'message': 'No suministró parámetros validos',
#                                       'action': 'Realice una nueva solicitud incluyendo status o role'})
#
#
# if __name__ == '__main__':
#     app.run(debug=True)
