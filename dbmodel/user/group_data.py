from api.apiconfig import app
import datetime

from sqlalchemy import and_


from dbmodel.dbconfig import s
from dbmodel.database_model import GroupModel
from dbmodel.user.membership_data import Membership, MembershipHistory



class Group(GroupModel):

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        membresia = self.membresia
        return {
            'id': self.id_grupo,
            'tipo': self.tipo_grupo.tipo_grupo,
            'nombre': self.nombre_grupo,
            'descripcion': self.descripcion,
            'creado': self.creado,
            'membresias': self.make_list(membresia)
        }

    @staticmethod
    def make_list(item_list):
        final_list = []
        for item in item_list:
            final_list.append(item.serialize)
        return final_list

    @staticmethod
    def check_item_exists(**kwargs):
        if 'name' in kwargs:
            item = s.query(Group).filter(and_(
                Group.nombre_grupo == kwargs['name'], Group.id_tipo_grupo == 1)).first()
            if item is None:
                return False
            return True
        if 'group' in kwargs:
            item = s.query(Group).filter(and_(
                Group.id_grupo == kwargs['group'], Group.id_tipo_grupo == 1)).first()
            if item is None:
                return False
            return True

    @staticmethod
    def get_item(item_id):
        item = s.query(Group).filter(
            Group.id_grupo == item_id).first()
        if not item:
            error = [404, {'message': 'Este grupo no existe',
                           'action': 'Realice una nueva consulta'}]
            return True, error
        return False, item

    @staticmethod
    def get_list():
        item_list = s.query(Group).all()
        if not item_list:
            error = [404, {'message': 'No existen grupos',
                           'action': 'Realice una nueva consulta'}]
            return True, error
        return False, item_list

    def add_item(self, user, id_type, name, description):
        if not (1 <= int(id_type) <= 3):
            mssg = [400, {'message': 'Error en los parámetros suministrados',
                          'action': 'Los valores aceptados son: 1: Publico, 2: Privado'}]
            return True, mssg
        if int(id_type) is 1 and self.check_item_exists(name=name):
            mssg = [409, {'message': 'Este grupo ya existe',
                          'action': 'Cambie el nombre del grupo'}]
            return True, mssg
        self.id_tipo_grupo = id_type
        self.nombre_grupo = name
        self.descripcion = description
        self.creado = datetime.datetime.now()
        membresia = Membership()
        s.add(self)
        s.flush()
        membresia.id_grupo = self.id_grupo
        membresia.id_rol_grupo = 1
        membresia.id_usuario = user
        historia = MembershipHistory()
        historia.id_estado_solicitud = 2
        s.add(membresia)
        s.flush()
        historia.id_actualizado_por = membresia.id_miembro
        membresia.historia.append(historia)
        self.membresia.append(membresia)
        s.add(self)
        s.commit()
        resp = [200, {'message': 'El grupo se ha creado exitosamente'}]
        return False, resp

    def modify_item(self, id_type, name, description, user):
        # Revisar si el usuario que realiza la actualización tiene credenciales de administrador
        # o si es el dueño de la membresia
        for miembro in self.membresia:
            if miembro.id_usuario is user:
                error, resp = miembro.get_role(self.id_grupo, user)
                if int(resp) is not 1 and int(resp) is not 2:
                    return True, [403, {'message': 'No cuenta con los permisos para realizar esta acción',
                                        'action': 'Realice otra consulta'}]
                self.id_tipo_grupo = id_type
                self.nombre_grupo = name
                self.descripcion = description
                s.commit()
                resp = [200, {'message': 'Los datos se actualizaron correctamente'}]
                return False, resp
        return True, [403, {'message': 'No cuenta con los permisos para realizar esta acción',
                            'action': 'Realice otra consulta'}]

    def delete_item(self, user):
        for miembro in self.membresia:
            if miembro.id_usuario is user:
                error, resp = miembro.get_role(self.id_grupo, user)
                if int(resp) is not 1 and int(resp) is not 2:
                    return True, [403, {'message': 'No cuenta con los permisos para realizar esta acción',
                                        'action': 'Realice otra consulta'}]
                s.delete(self)
                s.commit()
                resp = [200, {'message': 'El grupo se elimino correctamente'}]
                return False, resp
        return True, [403, {'message': 'No cuenta con los permisos para realizar esta acción',
                            'action': 'Realice otra consulta'}]


if __name__ == '__main__':
    app.run(debug=True)