from api.apiconfig import app
from sqlalchemy import Column, DateTime, Date, String, Integer, Boolean, ForeignKey, UniqueConstraint, Float, and_, or_, ForeignKeyConstraint, func, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import relationship, backref


from dbmodel.dbconfig import s
from dbmodel.database_model import MembershipModel, MembershipHistoryModel
from dbmodel.user.user_data import User
from dbmodel.user.group_data import Group



class Membership(MembershipModel):

    def __repr__(self):
        return '<Membresia %r>' % self.id_miembro

    """
    Este método convierte las instancias de esta clase en un diccionario.Con esto se puede
    convertir en JSON sin procesos posteriores.

    La variable local historia almacena el primer item de los resultados, el mas reciente,
    de la tabla historia_miembro asociados a esta membresia.
    """

    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        historia = self.historia[0]
        return {
            'id': self.id_miembro,
            'usuario': self.usuario.correo_electronico,
            'grupo': self.grupo.nombre_grupo,
            'estado': historia.estado_solicitud.estado_solicitud,
            'modificado': historia.creado,
            'rol': self.rol_grupo.rol_grupo
        }

    """ Verifica si existe una membresia del usuario 'user' asociada al grupo 'group'.
        Devuelve True si existe, False de otra manera
        """

    @staticmethod
    def check_item_exists(**kwargs):
        if 'user' in kwargs and 'group' in kwargs:
            item = s.query(Membership).filter(and_(
                Membership.id_usuario == kwargs['user'],
                Membership.id_grupo == kwargs['group'])).first()
            if item is None:
                return False
            return True
        elif 'membership' in kwargs:
            item = s.query(Membership).filter(
                Membership.id_miembro == kwargs['membership']).first()
            if item is None:
                return False
            return True

    """ Realiza una consulta a la tabla 'miembro' y devuelve los resultados asociados al
    usuario 'user'. Si no existen resultados para la consulta, se devuelve un error 404.
    Usando el parametro rq_user se verifica si el usuario que realiza la consulta, tiene
    permisos para acceder a los resultados. Si no se cuentan con los permisos necesarios
    se devuelve un error 403. De lo contrario se devuelve la lista que contiene todos
    los items del resultado de la consulta
    """
    @staticmethod
    def get_list_by_user(user, rq_user):
        item_list = s.query(Membership).filter(
            Membership.id_usuario == user).all()
        if rq_user is not user:
            error = [403, {'message': 'No cuenta con los permisos acceder a este recurso',
                           'action': 'Realice otra consulta'}]
            return True, error
        if not item_list:
            error = [404, {'message': 'No se encontraron membresias',
                           'action': 'Solicite la vinculacion a algun grupo o cree uno nuevo'}]
            return True, error
        return False, item_list

    """ Realiza una consulta a la tabla 'miembro' y devuelve los resultados asociados al
    grupo 'group'. Si no existen resultados para la consulta, se devuelve un error 404.

    Usando el parámetro 'user' se verifica si el usuario que realiza la consulta tiene
    permisos de administrador de grupo para acceder a los resultados. Si no se cuentan
    con los permisos necesarios se devuelve un error 403; Si no existen resultados de
    la consulta se devuelve un error 404 De lo contrario se devuelve la lista que
    contiene todos los items del resultado de la consulta.
    """

    def get_list_by_group(self, group, user):
        error, role = self.get_role(group, user)
        if error:
            resp = role
            return True, resp
        if role is not 1 and role is not 2:
            error = [403,
                     {'message': 'No cuenta con permisos de administrador o creador para aceder a este recurso',
                      'action': 'Solicite la vinculacion como administrador a este grupo'}]
            return True, error
        item_list = s.query(Membership).filter(Membership.id_grupo == group).all()
        if not item_list:
            error = [404, {'message': 'No se encontraron membresias activas en este grupo',
                           'action': 'Invite a sus contactos a unirse a este grupo'}]
            return True, error
        return False, item_list

    """ Realiza consulta en la tabla 'miembro' y devuelve los elementos
    relacionados con el grupo 'item_id' y el usuario 'user'.

    Si no existen resultados, se devuelve un error 404.
    """
    @staticmethod
    def get_item(item_id, user):
        item = s.query(Membership).filter(and_(
            Membership.id_grupo == item_id, Membership.id_usuario == user)).first()
        if not item:
            error = [404, {'message': 'Esta membresia no existe',
                           'action': 'Realice una nueva consulta'}]
            return True, error
        return False, item

    """  Crea un elemento en la tabla 'miembro'

    'Updated_by' se refiere a la membresia (Es decir usuario--grupo) que realiza la
    solicitud. Si no se suministra este parámetro se utiliza el valor de la
    membresia que esta por crearse, para eso se usa el método 'flush'. Este valor
    se almacena en la BD en la tabla historia_miembro accedida a través de la clase
    'MembershipHistory'.

    - Se evalua si el usuario al que se le creara la membresia existe, usando el
      metodo 'User.check_user_exists_by_id(user)'.
    - Se evalua si el usuario al que se le creara la membresia ya hace parte del
      grupo usando el metodo (self.check_item_exists'user=user, group=group)'.
    - Se evalua si el miembro que realiza la accion existe usando el metodo
      'self.check_item_exists(membership=updated_by)'.
    - Se evalua si los parametros 'user', 'group', 'role' y 'updated_by' fueron
      pasados en blanco.

    Se crea un nuevo elemento en la tabla 'historia_miembro' indicando la accion
    de crear un nuevo miebro.

    """
    def add_item(self, user, group, role, updated_by):
        error, mssg = User.check_user_exists_by_id(user)
        if error:
            return True, mssg
        if not Group.check_item_exists(group=group):
            mssg = [404, {'message': 'Este grupo no existe',
                          'action': 'Realice nuevamente la solicitud'}]
            return True, mssg
        if self.check_item_exists(user=user, group=group):
            mssg = [409, {'message': 'Este usuario ya hace parte de este grupo',
                          'action': 'Realice nuevamente la solicitud'}]
            return True, mssg
        if not self.check_item_exists(membership=updated_by):
            mssg = [400, {'message': 'Este miembro no existe',
                          'action': 'Realice nuevamente la solicitud'}]
            return True, mssg
        if not user:
            mssg = [400, {'message': 'El campo user no puede ser vacio o nulo',
                          'action': 'Ingrese un valor adecuado'}]
            return True, mssg
        if not group:
            mssg = [400, {'message': 'El campo group no puede ser vacio o nulo',
                          'action': 'Ingrese un valor adecuado'}]
            return True, mssg
        if not role:
            mssg = [400, {'message': 'El campo role no puede ser vacio o nulo',
                          'action': 'Ingrese un valor adecuado'}]
            return True, mssg
        if not updated_by:
            mssg = [400, {'message': 'El campo updated_by no puede ser vacio o nulo',
                          'action': 'Ingrese un valor adecuado'}]
            return True, mssg

        """ Asignacion de valores de esta clase """
        self.id_usuario = user
        self.id_grupo = group
        self.id_rol_grupo = role

        """ Asignacion de valores de la clase 'MembershipHistory' """
        historia = MembershipHistory()
        historia.id_estado_solicitud = 1
        if updated_by is None:
            s.add(self)
            s.flush()
            historia.id_actualizado_por = self.id_miembro
        else:
            historia.id_actualizado_por = updated_by
        self.historia = [historia]
        # if not (1 <= int(historia.id_estado_solicitud) <= 4):
        #     mssg = [400, {'message': 'Error en los parámetros suministrados',
        #                   'action': 'Los valores aceptados son: 1:Enviada, 2:Aceptada, 3:Negada, 4:Bloqueada'}]
        #     return True, mssg

        # error, resp = historia.get_most_recent(self.id_miembro)
        # if not error:
        #     if int(resp.id_estado_solicitud) == int(historia.id_estado_solicitud):
        #         error = [409, {'message': 'La membresia ya se encuentra en este estado',
        #                        'action': 'Realice nuevamente la solicitud cambiando los parametros'}]
        #         return True, error

        """ Se crea un nuevo registro de esta clase y de la clase 'MembershipHistory'

        Se llama 'commit()' una sola vez gracias al primary join especificado en
        la variable 'historia'.

        """
        s.add(self)
        s.commit()
        resp = [201, {'message': 'La membresia se ha creado exitosamente'}]
        return False, resp

    """ Consulta el rol del usuario 'user' en el grupo 'group'

    - Verifica si el usuario 'user' hace parte del grupo 'group', si no, devuelve un
      error 404
    """
    @staticmethod
    def get_role(group, user):
        item = s.query(Membership).filter(and_(
            Membership.id_grupo == group,
            Membership.id_usuario == user)).first()
        if not item:
            error = [404, {'message': 'No hace parte de este grupo o el grupo no existe',
                           'action': 'Solicite su vinculación a este grupo o realice una '
                                     'nueva consulta con un grupo existente'}]
            return True, error
        return False, item.id_rol_grupo

    """  Modifica el rol de la membresia en el grupo

    - Se evalua si los parametros 'user' y 'role' fueron
      pasados en blanco.
    - Verifica si el usuario que realiza la actualización tiene credenciales de
      administrador o creador usando el metodo self.get_role(self.id_grupo, user)
    - Verifica si la membresia ya cuenta con el rol al que se solicita la actualizacion,
      si es asi, devuelve un error 409
    """

    def role_change(self, role, user):
        if not user:
            mssg = [400, {'message': 'El campo user no puede ser vacio o nulo',
                          'action': 'Ingrese un valor adecuado'}]
            return True, mssg
        if not role:
            mssg = [400, {'message': 'El campo role no puede ser vacio o nulo',
                          'action': 'Ingrese un valor adecuado'}]
            return True, mssg
        error, resp = self.get_role(self.id_grupo, user)
        if error:
            return True, resp
        if int(resp) is not 1 and int(resp) is not 2:
            return True, [403, {'message': 'No cuenta con los permisos para realizar esta acción',
                                'action': 'Realice otra consulta'}]
        if not (1 <= int(role) <= 3):
            error = [400, {'message': 'Error en los parámetros suministrados',
                           'action': 'Los valores aceptados son: 1:Creador, 2:Admin, 3:Participante'}]
            return True, error
        if int(self.id_rol_grupo) is int(role):
            error = [409, {'message': 'Este usuario ya cuenta con este nivel de permisos',
                           'action': 'Realice nuevamente la solicitud'}]
            return True, error
        self.id_rol_grupo = role
        s.commit()
        resp = [200, {'message': 'El rol de este miembro se actualizo correctamente'}]
        return False, resp

    """ Crea un nuevo estado para la membresia actual en la tabla historia_miembro

    - Se evalua si los parametros 'user' y 'status' fueron
      pasados en blanco.
    - Revisar si el usuario que realiza la actualización tiene credenciales de
      administrador o si es el dueño de la membresia

    Crea una nueva instancia de la clase 'MembershipHistory' y crea un nuevo elemento
    """
    def new_status(self, status, user):
        if not user:
            mssg = [400, {'message': 'El campo user no puede ser vacio o nulo',
                          'action': 'Ingrese un valor adecuado'}]
            return True, mssg
        if not status:
            mssg = [400, {'message': 'El campo status no puede ser vacio o nulo',
                          'action': 'Ingrese un valor adecuado'}]
            return True, mssg
        error, resp = self.get_role(self.id_grupo, user)
        if self.id_usuario is not user and (int(resp) is not 1 and int(resp) is not 2):
            return True, [403, {'message': 'No cuenta con los permisos para realizar esta acción',
                                'action': 'Realice otra consulta'}]
        msstatus = MembershipHistory()
        error, mssg = msstatus.add_item(self.id_miembro, status, self.id_miembro)
        if error:
            return True, mssg
        return False, mssg

    def delete_item(self, user):
        # Revisar si el usuario que realiza la actualización tiene credenciales de administrador
        # o si es el dueño de la membresia
        error, resp = self.get_role(self.id_grupo, user)
        if self.id_usuario is not user:
            if int(resp) is not 1 and int(resp) is not 2:
                return True, [403, {'message': 'No cuenta con los permisos para realizar esta acción',
                                    'action': 'Realice otra consulta'}]
        s.delete(self)
        try:
            s.commit()
        except IntegrityError:
            s.rollback()
            s.flush()
            resp = [409, {'errores': {'message': 'La membresia no se puede eliminar',
                                      'action': 'Elimine los elementos relacionados e intente de nuevo'}}]
            return True, resp
        resp = [200, {'message': 'La membresia se elimino correctamente'}]
        return False, resp


class MembershipHistory(MembershipHistoryModel):

    def get_most_recent(self, ms):
        history_list = self.get_list_by_membership(ms)
        if not history_list:
            mssg = [404, {'message': 'Esta membresia no tiene historia',
                          'action': 'Realice una nueva consulta'}]
            return True, mssg
        return False, history_list[0]

    @staticmethod
    def get_list_by_membership(ms):
        return s.query(MembershipHistory).filter(
            MembershipHistory.id_miembro == ms).order_by(
            MembershipHistory.id_historia_miembro.desc()).all()

    def add_item(self, ms, request_status, rquser):
        if not (1 <= int(request_status) <= 4):
            mssg = [400, {'message': 'Error en los parametros suministrados',
                          'action': 'Los valores aceptados son: 1:Enviada, 2:Aceptada, 3:Negada, 4:Bloqueada'}]
            return True, mssg
        error, resp = self.get_most_recent(ms)
        if not error:
            if int(resp.id_estado_solicitud) == int(request_status):
                error = [409, {'message': 'La membresia ya se encuentra en este estado',
                               'action': 'Realice nuevamente la solicitud cambiando los parametros'}]
                return True, error
        self.id_miembro = ms
        self.id_estado_solicitud = request_status
        self.id_actualizado_por = rquser
        s.add(self)
        s.commit()
        resp = [200, {'message': 'El estado de la membresia se actualizo correctamente'}]
        return False, resp

if __name__ == '__main__':
    app.run(debug=True)