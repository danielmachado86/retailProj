import datetime

from sqlalchemy import and_, or_
from sqlalchemy.exc import IntegrityError

from dbmodel.dbconfig import s
from dbmodel.database_model import RelationshipModel, RelationshipStatusModel



class Relationship(RelationshipModel):

    def __repr__(self):
        return '<Relación %r>' % self.usuario_amigo

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        error, resp = RelationshipStatus().get_most_recent(self.id_relacion)
        return {
            'id': self.id_relacion,
            'usuario': self.usuario.correo_electronico,
            'amigo': self.usuario_amigo.correo_electronico,
            'estado': resp.estado_solicitud.estado_solicitud
        }

    @staticmethod
    def check_item_exists(user1, user2):
        item = s.query(Relationship).filter(or_(and_(
            Relationship.id_usuario == user1,
            Relationship.id_usuario_amigo == user2), and_(
            Relationship.id_usuario == user2,
            Relationship.id_usuario_amigo == user1))).first()
        if item is None:
                return False
        return True

    @staticmethod
    def get_list_by_user(user):
        item_list = s.query(Relationship).filter(
            Relationship.id_usuario == user).all()
        if not item_list:
            error = [404, {'message': 'No se encontraron relaciones',
                           'action': 'Encuentre a un amigo'}]
            return True, error
        return False, item_list

    @staticmethod
    def get_item(item_id):
        item = s.query(Relationship).filter(
            Relationship.id_relacion == item_id).first()
        if not item:
            error = [404, {'message': 'Esta relación no existe',
                           'action': 'Realice una nueva consulta'}]
            return True, error
        return False, item

    def add_item(self, user, friend):
        if self.check_item_exists(user, friend):
            error = [409, {'message': 'Esta relación ya existe',
                           'action': 'Realice nuevamente la solicitud'}]
            return True, error
        self.id_usuario = user
        self.id_usuario_amigo = friend
        s.add(self)
        s.commit()

        # Crea estado de solicitud
        error, mssg = RelationshipStatus().add_item(self.id_relacion, 1)
        if error:
            return True, mssg
        resp = [201, {'message': 'La relación se ha creado exitosamente'}]
        return False, resp

    def modify_item(self, status):
        rsstatus = RelationshipStatus()
        error, mssg = rsstatus.add_item(self.id_relacion, status)
        if error:
            return True, mssg
        return False, mssg

    def delete_item(self):
        s.delete(self)
        try:
            s.commit()
        except IntegrityError:
            s.rollback()
            s.flush()
            resp = [409, {'errores': {'message': 'La relacion no se puede eliminar',
                                      'action': 'Elimine los elementos relacionados e intente de nuevo'}}]
            return True, resp
        resp = [200, {'message': 'La relacion se elimino correctamente'}]
        return False, resp


class RelationshipStatus(RelationshipStatusModel):

    def get_most_recent(self, rs):
        status_list = self.get_list_by_relationship(rs)
        if not status_list:
            mssg = [404, {'message': 'Esta relacion no tiene historia',
                          'action': 'Realice una nueva consulta'}]
            return True, mssg
        return False, status_list[0]

    @staticmethod
    def get_list_by_relationship(rs):
        return s.query(RelationshipStatus).filter(
            RelationshipStatus.id_relacion == rs).order_by(
            RelationshipStatus.id_estado_relacion.desc()).all()

    def add_item(self, rs, request_status):
        if not (1 <= int(request_status) <= 4):
            mssg = [400, {'message': 'Error en los parametros suministrados',
                          'action': 'Los valores aceptados son: 1:Enviada, 2:Aceptada, 3:Negada, 4:Bloqueada'}]
            return True, mssg
        error, resp = self.get_most_recent(rs)
        if not error:
            if int(resp.id_estado_solicitud) == int(request_status):
                error = [409, {'message': 'La relacion ya se encuentra en este estado',
                               'action': 'Realice nuevamente la solicitud cambiando los parametros'}]
                return True, error
        self.id_relacion = rs
        self.id_estado_solicitud = request_status
        self.creado = datetime.datetime.now()
        s.add(self)
        s.commit()
        resp = [200, {'message': 'El estado de la relacion se actualizo correctamente'}]
        return False, resp

