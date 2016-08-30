import calendar
import datetime

import re

from unidecode import unidecode
import bcrypt
from geoalchemy2 import Geometry
from sqlalchemy import Column, DateTime, Date, String, Integer, Boolean, ForeignKey, UniqueConstraint, Float, and_, or_, ForeignKeyConstraint, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import relationship, backref
from dbmodel.dbconfig import Base, s
from itsdangerous import(TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)
import random
import string


secret_key = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(32))

Base.metadata.schema = 'usuario'

'''Social'''


class Relationship(Base):
    __tablename__ = 'relacion'

    id_relacion = Column(Integer, primary_key=True)
    id_usuario = Column(Integer, ForeignKey('usuario.id_usuario'), nullable=False)
    id_usuario_amigo = Column(Integer, ForeignKey('usuario.id_usuario'), nullable=False)

    __table_args__ = (UniqueConstraint('id_usuario', 'id_usuario_amigo', name='relacion_unica'),)

    usuario = relationship("User", foreign_keys=[id_usuario])
    usuario_amigo = relationship("User", foreign_keys=[id_usuario_amigo])

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


class RelationshipStatus(Base):
    __tablename__ = 'estado_relacion'

    id_estado_relacion = Column(Integer, primary_key=True)
    id_relacion = Column(Integer, ForeignKey('relacion.id_relacion'), nullable=False)
    id_estado_solicitud = Column(Integer, ForeignKey('estado_solicitud.id_estado_solicitud'), nullable=False)
    creado = Column(DateTime(timezone=True))

    relacion = relationship("Relationship", foreign_keys=[id_relacion])
    estado_solicitud = relationship("RequestStatus", foreign_keys=[id_estado_solicitud])

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


'''Social'''

'''Membership'''


class Membership(Base):
    __tablename__ = 'miembro'

    """Definición de campos en base de datos"""

    id_miembro = Column(Integer, primary_key=True)
    id_usuario = Column(Integer, ForeignKey('usuario.id_usuario'), nullable=False)
    id_grupo = Column(Integer, ForeignKey('grupo.id_grupo'), nullable=False)
    id_rol_grupo = Column(Integer, ForeignKey('rol_grupo.id_rol_grupo'), nullable=False)
    usuario = relationship("User", foreign_keys=[id_usuario])
    rol_grupo = relationship("Role", foreign_keys=[id_rol_grupo])
    """
    la variable historia almacena los resultados de la tabla historia_miembro asociados
    a esta membresia usando una clausula JOIN. Los resultados se ordenan con la columna
    'creado' de manera descendiente. Se especifica un backref a tabla 'miembro'. Esto
    permite acceder a 'miembro' desde historia_miembro sin realizar consulta.
    """

    historia = relationship('MembershipHistory', order_by="desc(MembershipHistory.creado)",
                            primaryjoin="Membership.id_miembro==MembershipHistory.id_miembro",
                            backref=backref('miembro', uselist=False), cascade="all, delete-orphan", lazy='subquery')

    __table_args__ = (UniqueConstraint('id_usuario', 'id_grupo', name='miembro_unica'),)

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

        Se hace llama 'commit()' una sola vez gracias al primary join especificado en
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


class MembershipHistory(Base):
    __tablename__ = 'historia_miembro'

    id_historia_miembro = Column(Integer, primary_key=True)
    id_miembro = Column(Integer, ForeignKey('miembro.id_miembro'), nullable=False)
    id_estado_solicitud = Column(Integer, ForeignKey('estado_solicitud.id_estado_solicitud'), nullable=False)
    id_actualizado_por = Column(Integer, ForeignKey('miembro.id_miembro'), nullable=False)
    creado = Column(DateTime(timezone=True), nullable=False)
    estado_solicitud = relationship("RequestStatus", foreign_keys=[id_estado_solicitud])
    actualizado_por = relationship("Membership", foreign_keys=[id_actualizado_por])

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


class Group(Base):
    __tablename__ = 'grupo'

    id_grupo = Column(Integer, primary_key=True)
    id_tipo_grupo = Column(Integer, ForeignKey('tipo_grupo.id_tipo_grupo'), nullable=False)
    nombre_grupo = Column(String, nullable=False)
    descripcion = Column(String, nullable=False)
    creado = Column(DateTime(timezone=True), nullable=False)
    tipo_grupo = relationship("GroupType", foreign_keys=[id_tipo_grupo])
    membresia = relationship('Membership', primaryjoin="Group.id_grupo==Membership.id_grupo",
                             backref=backref('grupo', uselist=False), cascade="all, delete-orphan", lazy='subquery')

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


class GroupType(Base):
    __tablename__ = 'tipo_grupo'

    id_tipo_grupo = Column(Integer, primary_key=True)
    tipo_grupo = Column(String, nullable=False)


class Role(Base):
    __tablename__ = 'rol_grupo'

    id_rol_grupo = Column(Integer, primary_key=True)
    rol_grupo = Column(String, nullable=False)
'''Membership'''

'''Common'''


class RequestStatus(Base):
    __tablename__ = 'estado_solicitud'

    id_estado_solicitud = Column(Integer, primary_key=True)
    estado_solicitud = Column(String, nullable=False)
'''Common'''

'''User'''


class AuthenticationType(Base):
    __tablename__ = 'tipo_autenticacion'

    id_tipo_autenticacion = Column(Integer, primary_key=True)
    tipo_autenticacion = Column(String, nullable=False)


class User(Base):
    __tablename__ = 'usuario'

    id_usuario = Column(Integer, primary_key=True)
    id_tipo_autenticacion = Column(Integer, ForeignKey('tipo_autenticacion.id_tipo_autenticacion'), nullable=False)
    nombre_completo = Column(String, nullable=False)
    correo_electronico = Column(String, unique=True, index=True, nullable=False)
    numero_movil = Column(String, unique=True, index=True, nullable=False)
    nombre_usuario = Column(String, unique=True, index=True, nullable=False)
    contrasena_hash = Column(String, nullable=True)
    contrasena_salt = Column(String, nullable=True)
    verificado = Column(Boolean, default=False, nullable=False)
    modificado = Column(DateTime(timezone=True), nullable=False)

    tipo_autenticacion = relationship("AuthenticationType", foreign_keys=[id_tipo_autenticacion])

    def __repr__(self):
        return '<Usuario %r>' % self.correo_electronico

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id_usuario,
            'nombre': self.nombre_completo,
            'username': self.nombre_usuario
        }

    def username_generator(self, name, size=6, chars=string.digits):
        name = unidecode(name).lower()
        nameproc = name.split(" ")
        if nameproc.__len__() >= 2:
            name = nameproc[0] + '-' + nameproc[1]
        elif nameproc.__len__() == 1:
            name = nameproc[0]
        else:
            name = 'retailproj'
        username = name + "-" + ''.join(random.choice(chars) for _ in range(size))
        exists, mssg = self.check_user_exists_by_username(username)
        if exists:
            try:
                return self.username_generator(name)
            except RecursionError:
                return self.username_generator(name, size=size + 1)
        return username

    def generate_auth_token(self, expiration=600):
        serial = Serializer(secret_key, expires_in=expiration)
        return serial.dumps({'id': self.id_usuario})

    @staticmethod
    def verify_auth_token(token):
        serial = Serializer(secret_key)
        try:
            data = serial.loads(token)
        except SignatureExpired:
            # Valid Token, but expired
            return None
        except BadSignature:
            # Invalid Token
            return None
        return data['id']

    @staticmethod
    def check_user_exists_by_id(item_id):
        if not item_id:
            mssg = [400, {'message': 'El campo item_id no puede ser vacio o nulo',
                          'action': 'Ingrese un valor adecuado'}]
            return True, mssg
        if not isinstance(item_id, int):
            mssg = [400, {'message': 'El valor del campo item_id debe ser un numero entero',
                          'action': 'Ingrese un valor adecuado'}]
            return True, mssg
        if s.query(User).filter(User.id_usuario == item_id).first():
            mssg = [409, {'message': 'Este usuario existe'}]
            return True, mssg
        mssg = [200, {'message': 'Este usuario no existe'}]
        return False, mssg

    @staticmethod
    def check_user_exists_by_mail(mail):
        if not mail:
            mssg = [400, {'message': 'El campo mail no puede ser vacío o nulo',
                          'action': 'Ingrese un valor adecuado'}]
            return True, mssg
        if s.query(User).filter(User.correo_electronico == mail).first():
            mssg = [409, {'message': 'Este usuario existe'}]
            return True, mssg
        mssg = [200, {'message': 'Este usuario no existe'}]
        return False, mssg

    @staticmethod
    def check_user_exists_by_username(username):
        if s.query(User).filter(User.nombre_usuario == username).first():
            mssg = [409, {'message': 'Este usuario existe'}]
            return True, mssg
        mssg = [200, {'message': 'Este usuario no existe'}]
        return False, mssg

    @staticmethod
    def check_user_exists_by_phone(phone):
        if not phone:
            mssg = [400, {'message': 'El campo phone no puede ser vacio o nulo',
                          'action': 'Ingrese un valor adecuado'}]
            return True, mssg
        if s.query(User).filter(User.numero_movil == phone).first():
            mssg = [409, {'message': 'Este usuario existe'}]
            return True, mssg
        mssg = [409, {'message': 'Este usuario existe'}]
        return False, mssg

    @staticmethod
    def get_item_by_mail(mail, auth_type):
        if not mail:
            return None
        if not isinstance(auth_type, int):
            return None
        if not (1 <= int(auth_type) <= 3):
            return None
        return s.query(User).filter(and_(
            User.correo_electronico == mail,
            User.id_tipo_autenticacion == auth_type)).first()

    @staticmethod
    def get_item(id_user):
        if not isinstance(id_user, int):
            return None
        return s.query(User).filter(
            User.id_usuario == id_user).first()

    def verify_password(self, password):
        if self is None:
            return False
        if self.contrasena_hash == bcrypt.hashpw(
                password.encode('utf-8'), self.contrasena_salt.encode('utf-8')
        ).decode("utf-8"):
            return True

    def add_item(self, name, mail, phone, password, picture, auth_type):
        if not name:
            mssg = [400, {'message': 'El campo name no puede ser vacio o nulo',
                          'action': 'Ingrese un valor adecuado'}]
            return True, mssg
        if re.match("[a-zA-Z0-9]+", unidecode(name).replace(" ", "")) is None:
            mssg = [400, {'message': 'El campo name debe tener al menos una letra o numero',
                          'action': 'Ingrese un valor adecuado'}]
            return True, mssg
        if not mail:
            mssg = [400, {'message': 'El campo mail no puede ser vacio o nulo',
                          'action': 'Ingrese un valor adecuado'}]
            return True, mssg
        if not phone:
            mssg = [400, {'message': 'El campo phone no puede ser vacio o nulo',
                          'action': 'Ingrese un valor adecuado'}]
            return True, mssg
        error, resp = self.check_user_exists_by_mail(mail)
        if error:
            return True, resp
        error, resp = self.check_user_exists_by_phone(phone)
        if error:
            return True, resp
        if not (1 <= int(auth_type) <= 3):
            mssg = [400, {'message': 'Error en los parámetros suministrados',
                          'action': 'Los valores aceptados son: 1: Local, 2: Google, 3: Facebook'}]
            return True, mssg
        if auth_type == 1 and (password is None or password is ''):
            error = [400, {'message': 'La contraseña no cuenta con las características requeridas',
                           'action': 'Vuelva a intentarlo ingresando una contraseña valida'}]
            return True, error
        self.nombre_completo = name
        self.correo_electronico = mail
        self.numero_movil = phone
        self.nombre_usuario = self.username_generator(name)
        self.id_tipo_autenticacion = auth_type
        salt = bcrypt.gensalt(10)
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        self.contrasena_hash = hashed.decode('utf-8')
        self.contrasena_salt = salt.decode('utf-8')
        s.add(self)
        s.commit()

        # Crear imagen predeterminada
        UserImage().add_item(
            self.id_usuario, '', picture)
        resp = [201, {'message': 'El usuario se ha creado exitosamente'}]
        return False, resp

    def verify_account(self):
        if self.verificado:
            mssg = [409, {'message': 'La cuenta ya se encuentra verificada'}]
            return True, mssg
        self.verificado = True
        s.commit()
        mssg = [200, {'message': 'La cuenta se verifico exitosamente'}]
        return False, mssg

    def modify_item(self, name, mail, phone, password):
        if self.correo_electronico != mail:
            if self.check_user_exists_by_mail(mail) or self.check_user_exists_by_phone(phone):
                error = [409, {'message': 'Este usuario ya existe',
                               'action': 'Ingrese con las credenciales o utilice otro correo o teléfono'}]
                return True, error
        if self.id_tipo_autenticacion == 1 and (password is None or password is ''):
            error = [400, {'message': 'La contraseña no cuenta con las características requeridas',
                           'action': 'Vuelva a intentarlo ingresando una contraseña valida'}]
            return True, error
        salt = self.contrasena_salt
        hashed = bcrypt.hashpw(
            password.encode('utf-8'),
            salt.encode('utf-8')).decode("utf-8")
        self.nombre_completo = name
        self.correo_electronico = mail
        self.numero_movil = phone
        self.contrasena_hash = hashed
        s.commit()
        resp = [200, {'message': 'Los datos se actualizaron correctamente'}]
        return False, resp

    def modify_name(self, name):
        if not name:
            mssg = [400, {'message': 'El campo name no puede ser vacio o nulo',
                          'action': 'Ingrese un valor adecuado'}]
            return True, mssg
        if re.match("[a-zA-Z0-9]+", unidecode(name).replace(" ", "")) is None:
            mssg = [400, {'message': 'El campo name debe tener al menos una letra o numero',
                          'action': 'Ingrese un valor adecuado'}]
            return True, mssg
        self.nombre_completo = name
        s.commit()
        resp = [200, {'message': 'El nombre se actualizó correctamente'}]
        return False, resp

    def change_username(self, username):
        if not username:
            mssg = [400, {'message': 'El campo username no puede ser vacio o nulo',
                          'action': 'Ingrese un valor adecuado'}]
            return True, mssg
        if re.match("[ ]+", username):
            mssg = [400, {'message': 'El campo username debe tener al menos una letra o numero',
                          'action': 'Ingrese un valor adecuado'}]
            return True, mssg
        self.nombre_usuario = username
        s.commit()
        resp = [200, {'message': 'El nombre de usuario se actualizó correctamente'}]
        return False, resp

    def change_password(self, password):
        if self.id_tipo_autenticacion != 1:
            error = [400, {'message': 'Su cuenta utiliza un servicio de terceros para autenticación',
                           'action': 'Realice el cambio en su cuenta de google o Facebook'}]
            return True, error
        if password is None or password is '':
            error = [400, {'message': 'La contraseña no cuenta con las características requeridas',
                           'action': 'Vuelva a intentarlo ingresando una contraseña valida'}]
            return True, error
        salt = bcrypt.gensalt(10)
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        self.contrasena_hash = hashed.decode('utf-8')
        self.contrasena_salt = salt.decode('utf-8')
        s.add(self)
        s.commit()
        resp = [200, {'message': 'La contraseña se actualizó correctamente'}]
        return False, resp

    def delete_item(self):
        s.delete(self)
        s.commit()
        resp = [200, {'message': 'El usuario se elimino correctamente'}]
        return False, resp


class UserImage(Base):
    # __table_args__ = {'schema': 'usuario'}
    __tablename__ = 'imagen_usuario'

    id_imagen_usuario = Column(Integer, primary_key=True)
    id_usuario = Column(Integer, ForeignKey('usuario.id_usuario'), nullable=False)
    descripcion = Column(String, nullable=False)
    url = Column(String, nullable=False)
    usuario = relationship("User", foreign_keys=[id_usuario])

    def add_item(self, user, description, url):
        self.id_usuario = user
        self.descripcion = description
        self.url = url
        s.add(self)
        s.commit()
        return True

'''User'''

'''Location'''


class UserLocation(Base):
    __tablename__ = 'direccion_usuario'

    id_direccion = Column(Integer, primary_key=True)
    id_usuario = Column(Integer, ForeignKey('usuario.id_usuario'), index=True, nullable=False)
    id_ciudad_usuario = Column(Integer, ForeignKey('ciudad_usuario.id_ciudad_usuario'), nullable=False)
    nombre_favorito = Column(String, nullable=True)
    coordenadas = Column(Geometry(geometry_type='POINT'), nullable=False)
    direccion = Column(String, nullable=False)
    referencia = Column(String, nullable=False)
    fecha_registro = Column(DateTime(timezone=True), nullable=False)
    favorito = Column(Boolean, nullable=False)

    usuario = relationship("User", foreign_keys=[id_usuario])
    ciudad = relationship("City", foreign_keys=[id_ciudad_usuario])

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id_direccion': self.id_direccion,
            'usuario': self.usuario.nombre_completo,
            'ciudad': self.ciudad.ciudad,
            'pais': self.ciudad.pais_usuario.nombre_pais,
            'continente': self.ciudad.pais_usuario.continente.nombre_continente,
            'nombre': self.nombre_favorito,
            'coordenadas': self.coordenadas,
            'direccion': self.direccion,
            'referencia': self.referencia,
            'fecha': self.fecha_registro.strftime("%Y-%m-%d"),
            'favorito': self.favorito
        }

    @staticmethod
    def get_item(item_id):
        location_item = s.query(UserLocation,
                                 func.ST_X(UserLocation.coordenadas),
                                 func.ST_Y(UserLocation.coordenadas),
                                 func.ST_AsText(UserLocation.coordenadas)
                                 ).filter(UserLocation.id_direccion == item_id).first()
        location_item[0].coordenadas = '{}, {}'.format(location_item[1], location_item[2])
        location_item = location_item[0]
        if not location_item:
            location_error = [404, {'message': 'Esta direccion no existe',
                                     'action': 'Realice una nueva consulta'}]
            return True, location_error
        return False, location_item

    def add_item(self, user, city, name, location, address, reference):
        self.id_usuario = user
        self.id_ciudad_usuario = city
        self.nombre_favorito = name
        self.coordenadas = 'POINT({} {})'.format(location[0], location[1])
        self.direccion = address
        self.referencia = reference
        self.fecha_registro = datetime.datetime.now()
        self.favorito = False
        s.add(self)
        s.commit()
        resp = [201, {'message': 'La dirección se ha creado exitosamente'}]
        return False, resp


class Country(Base):
    __tablename__ = 'pais_usuario'

    id_pais_usuario = Column(Integer, primary_key=True)
    locale = Column(String, nullable=False)
    id_continente_usuario = Column(Integer, ForeignKey('continente_usuario.id_continente_usuario'), nullable=False)
    codigo_pais_iso = Column(String, nullable=False)
    nombre_pais = Column(String, nullable=False)
    continente = relationship("Continent", foreign_keys=[id_continente_usuario])


class Continent(Base):
    __tablename__ = 'continente_usuario'

    id_continente_usuario = Column(Integer, primary_key=True)
    codigo_continente = Column(String, nullable=False)
    nombre_continente = Column(String, nullable=False)
    locale = Column(String, nullable=False)


class City(Base):
    __tablename__ = 'ciudad_usuario'

    id_ciudad_usuario = Column(Integer, primary_key=True)
    id_pais_usuario = Column(Integer, ForeignKey('pais_usuario.id_pais_usuario'), nullable=False)
    ciudad = Column(String, nullable=False)
    codigo_ciudad_iso = Column(String, nullable=False)
    pais_usuario = relationship("Country", foreign_keys=[id_pais_usuario])

'''Location'''

'''Subscription'''


class SubscriptionGroup(Base):
    __tablename__ = 'grupo_suscripcion'

    id_grupo_suscripcion = Column(Integer, primary_key=True)
    id_plan_suscripcion = Column(Integer, ForeignKey('plan_suscripcion.id_plan'), nullable=False)
    id_estado_suscripcion = Column(Integer, nullable=False)
    fecha_inicio = Column(DateTime(timezone=True), nullable=False)
    renovar = Column(Boolean, nullable=False)
    plan_suscripcion = relationship("SubscriptionPlan", foreign_keys=[id_plan_suscripcion])

    miembro = relationship('SubscriptionMember', primaryjoin="SubscriptionGroup.id_grupo_suscripcion==SubscriptionMember.id_grupo_suscripcion",
                           backref=backref('grupo_suscripcion', uselist=False), cascade="all, delete-orphan", lazy='subquery')

    orden = relationship('SubscriptionOrder',
                         primaryjoin="SubscriptionGroup.id_grupo_suscripcion==SubscriptionOrder.id_grupo_suscripcion",
                         backref=backref('grupo_suscripcion', uselist=False), cascade="all, delete-orphan",
                         lazy='subquery')

    def get_subscription_status(self):
        subscription_status = {1: 'Activa',
                               2: 'Degradada',
                               3: 'Pendiente'}
        return subscription_status.get(self.id_estado_suscripcion)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        miembro = self.miembro
        orden = self.orden
        return {
            'id_suscripcion': self.id_grupo_suscripcion,
            'plan': self.plan_suscripcion.serialize,
            'estado': self.get_subscription_status(),
            'fecha_inicio': self.fecha_inicio.strftime("%Y-%m-%d %H:%M:%S %Z"),
            'fecha_final': self.get_end_date(self.fecha_inicio, self.plan_suscripcion.duracion_plan).strftime("%Y-%m-%d %H:%M:%S %Z"),
            'fecha_renovarl': self.get_renew_date(self.fecha_inicio, self.plan_suscripcion.duracion_plan).strftime("%Y-%m-%d %H:%M:%S %Z"),
            'renovar': self.renovar,
            'miembros': self.make_list(miembro),
            'orden': self.make_list(orden)
        }

    @staticmethod
    def make_list(item_list):
        final_list = []
        for item in item_list:
            final_list.append(item.serialize)
        return final_list

    def compare_number_members(self, plan):
        error, resp = SubscriptionPlan.get_number_members(plan)
        return resp-len(self.miembro)

    @staticmethod
    def get_item(item_id):
        item = s.query(SubscriptionGroup).filter(
            SubscriptionGroup.id_grupo_suscripcion == item_id).first()
        if not item:
            error = [404, {'message': 'Este grupo no existe',
                           'action': 'Realice una nueva consulta'}]
            return True, error
        return False, item

    def get_end_date(self, start_date, plan_duration):
        return self.get_renew_date(start_date, plan_duration) - datetime.timedelta(days=1)

    @staticmethod
    def get_renew_date(start_date, plan_duration):
        month = start_date.month - 1 + plan_duration
        year = int(start_date.year + month / 12)
        month = month % 12 + 1
        day = min(start_date.day, calendar.monthrange(year, month)[1])
        return start_date.replace(year, month, day)

    def renew_subscription(self, payment_info):
        payment_info[1]['currency'] = self.plan_suscripcion.moneda
        payment_info[1]['amount'] = self.plan_suscripcion.precio_plan
        from dbmodel.order.ordermodel import SubscriptionOrder  # Relation-Import
        orden = SubscriptionOrder(self.id_grupo_suscripcion, payment_info)
        self.orden.append(orden)
        if self.orden[0].transaccion[0].id_estado_transaccion == 2:
            self.id_estado_suscripcion = 1
            self.fecha_inicio = self.get_renew_date(self.fecha_inicio, self.plan_suscripcion.duracion_plan)
            error, resp = False, [201, {'message': 'La suscripción se ha renovado exitosamente'}]
            s.add(self)
            s.commit()
            return error, resp
        elif self.orden[0].transaccion[0].id_estado_transaccion == 3:
            self.id_estado_suscripcion = 2
            error, resp = True, [201, {'message': 'El pago fue rechazado, se establece la '
                                                  'suscripción en plan gratuito',
                                       'action': 'Intente realizar el pago de nuevo'}]
            s.add(self)
            s.commit()
            return error, resp

    def add_item(self, plan, user, payment_info=None):
        self.id_plan_suscripcion = 1
        self.id_estado_suscripcion = 1
        self.renovar = True
        self.fecha_inicio = datetime.datetime.now()
        s.add(self)
        s.flush()
        miembro = SubscriptionMember.create(self.id_grupo_suscripcion, user)
        self.miembro.append(miembro)
        error, resp = False, [201, {'message': 'La suscripción se ha creado exitosamente'}]
        if plan != 1 and payment_info is not None:
            self.id_plan_suscripcion = plan
            payment_info[1]['currency'] = self.plan_suscripcion.moneda
            payment_info[1]['amount'] = self.plan_suscripcion.precio_plan
            from dbmodel.order.ordermodel import SubscriptionOrder  # Relation-Import
            orden = SubscriptionOrder(self.id_grupo_suscripcion, payment_info)
            self.orden.append(orden)
            if self.orden[0].transaccion[0].id_estado_transaccion == 2:
                self.id_estado_suscripcion = 1
                error, resp = False, [201, {'message': 'La suscripción se ha creado exitosamente'}]
            elif self.orden[0].transaccion[0].id_estado_transaccion == 3:
                self.id_estado_suscripcion = 2
                error, resp = True, [201, {'message': 'El pago fue rechazado, se establece la '
                                                      'suscripción en plan gratuito',
                                           'action': 'Intente realizar el pago de nuevo'}]
        s.add(self)
        s.commit()
        return error, resp

    def change_item(self, plan, payment_info=None):
        if plan == self.id_plan_suscripcion:
            error, resp = False, [409, {'message': 'La suscripcion no se cambio porque ya se encuentra en este plan',
                                        'action': 'Seleccione un plan diferente al actual'}]
            return error, resp

        if self.compare_number_members(plan) < 0:
            error, resp = False, [409, {'message': 'La suscripcion no se cambio porque la cantidad de usuarios '
                                                   'activos es mayor a la permitida en el nuevo plan',
                                        'action': 'Seleccione un plan diferente al actual '
                                                  'o elimine usuarios de la suscripcion'}]
            return error, resp

        if plan == 1:
            self.id_plan_suscripcion = plan
            self.id_estado_suscripcion = 1
            self.renovar = True
            self.fecha_inicio = datetime.datetime.now()
            error, resp = False, [201, {'message': 'La suscripción se ha cambiado exitosamente'}]
            s.add(self)
            s.commit()
            return error, resp
        elif plan >= 2 and payment_info is not None:
            self.id_plan_suscripcion = plan
            payment_info[1]['currency'] = self.plan_suscripcion.moneda
            payment_info[1]['amount'] = self.plan_suscripcion.precio_plan
            from dbmodel.order.ordermodel import SubscriptionOrder  # Relation-Import
            orden = SubscriptionOrder(self.id_grupo_suscripcion, payment_info)
            self.orden.append(orden)
            print(self.orden[0].transaccion[0].id_estado_transaccion)
            if self.orden[0].transaccion[0].id_estado_transaccion == 2:
                self.id_estado_suscripcion = 1
                error, resp = False, [201, {'message': 'La suscripción se ha cambiado exitosamente'}]
                s.add(self)
                s.commit()
                return error, resp
            elif self.orden[0].transaccion[0].id_estado_transaccion == 3:
                self.id_estado_suscripcion = 2
                error, resp = True, [201, {'message': 'El pago fue rechazado, se establece la '
                                                      'suscripción en plan gratuito',
                                           'action': 'Realice el pago de nuevo'}]
                s.add(self)
                s.commit()
                return error, resp

    def change_suscription_plan(self, plan):
        self.plan_suscripcion = plan
        s.add(self)
        s.commit()

    def toggle_suscription_renew(self):
        if self.renovar is True:
            self.renovar = False
        else:
            self.renovar = True
        s.add(self)
        s.commit()


class SubscriptionMember(Base):
    __tablename__ = 'miembro_suscripcion'

    id_miembro_suscripcion = Column(Integer, primary_key=True)
    id_usuario = Column(Integer, ForeignKey('usuario.id_usuario'), nullable=False)
    id_grupo_suscripcion = Column(Integer, ForeignKey('grupo_suscripcion.id_grupo_suscripcion'), nullable=False)
    titular = Column(Boolean, nullable=False)
    usuario = relationship("User", foreign_keys=[id_usuario])
    # grupo_suscripcion = relationship("SubscriptionGroup", foreign_keys=[id_grupo_suscripcion])

    __table_args__ = (UniqueConstraint('id_usuario', 'id_grupo_suscripcion', name='miembro_suscripcion_unico'),)

    historia = relationship(
        'SubscriptionMemberHistory',
        primaryjoin="SubscriptionMember.id_miembro_suscripcion==SubscriptionMemberHistory.id_miembro_suscripcion",
        backref=backref('miembro_suscripcion', uselist=False),
        cascade="all, delete-orphan", lazy='subquery'
    )

    @classmethod
    def create(cls, group, user):
        obj = cls()
        obj.id_usuario = user
        obj.id_grupo_suscripcion = group
        obj.titular = True

        s.add(obj)
        s.flush()

        s.add(SubscriptionMemberHistory(obj.id_miembro_suscripcion, 2, obj.id_miembro_suscripcion))
        return obj

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id_miembro': self.id_miembro_suscripcion,
            'usuario': self.usuario.nombre_completo,
            'titular': self.titular,
            'estado': self.historia[0].get_subscription_member_status()
        }

    def add_item(self, group, user):
        error, item = SubscriptionGroup().get_item(group)
        if error:
            mssg = item
            return True, mssg
        if len(item.miembro) >= item.plan_suscripcion.cantidad_beneficiarios:
            error = [404, {'message': 'Se ha alcanzado el limite de beneficiarios para este plan',
                           'action': 'Elimine beneficiarios o actualice su plan'}]
            return True, error
        self.id_usuario = user
        self.id_grupo_suscripcion = group
        self.titular = False

        s.add(self)
        s.flush()
        history = SubscriptionMemberHistory(self.id_miembro_suscripcion, 1, self.id_miembro_suscripcion)
        s.add(history)
        s.commit()
        resp = [201, {'message': 'El miembro de la suscripción se ha creado exitosamente'}]
        return False, resp

    def delete_item(self):
        s.delete(self)
        s.commit()
        resp = [201, {'message': 'El miembro de la suscripción se ha eliminado exitosamente'}]
        return False, resp


class SubscriptionMemberHistory(Base):
    __tablename__ = 'historia_miembro_suscripcion'

    id_historia_miembro_suscripcion = Column(Integer, primary_key=True)
    id_miembro_suscripcion = Column(Integer, ForeignKey('miembro_suscripcion.id_miembro_suscripcion'), nullable=False)
    id_estado_miembro_suscripcion = Column(Integer, nullable=False)
    id_actualizado_por = Column(Integer, ForeignKey('miembro_suscripcion.id_miembro_suscripcion'), nullable=False)
    fecha_actualizacion = Column(DateTime(timezone=True), nullable=False)
    actualizado_por = relationship("SubscriptionMember", foreign_keys=[id_actualizado_por])

    def __init__(self, member, state, updated_by):
        self.id_miembro_suscripcion = member
        self.id_estado_miembro_suscripcion = state
        self.id_actualizado_por = updated_by
        self.fecha_actualizacion = datetime.datetime.now()

    def get_subscription_member_status(self):
        subscription_member_status = {1: 'Pendiente',
                                      2: 'Activo',
                                      3: 'Declinado',
                                      4: 'Retirado'}
        return subscription_member_status.get(self.id_estado_miembro_suscripcion)


class MembershipSubscriptionStatus(Base):
    __tablename__ = 'estado_miembro_suscripcion'

    id_estado_miembro_suscripcion = Column(Integer, primary_key=True)
    estado_miembro_suscripcion = Column(String, nullable=False)


class SubscriptionPlan(Base):
    __tablename__ = 'plan_suscripcion'

    id_plan = Column(Integer, primary_key=True)
    nombre_plan = Column(String, nullable=False)
    cantidad_beneficiarios = Column(Integer, nullable=False)
    limite_servicios = Column(Integer, nullable=False)
    moneda = Column(String, nullable=False)
    precio_plan = Column(Integer, nullable=False)
    duracion_plan = Column(Integer, nullable=False)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id_plan': self.id_plan,
            'nombre': self.nombre_plan,
            'cantidad_miembros': self.cantidad_beneficiarios,
            'limite_servicios': self.limite_servicios,
            'precio_plan': self.precio_plan,
            'duracion_plan': self.duracion_plan
        }

    @staticmethod
    def get_number_members(item_id):
        item = s.query(SubscriptionPlan).filter(
            SubscriptionPlan.id_plan == item_id).first()
        if not item:
            error = [404, {'message': 'Este plan no existe',
                           'action': 'Realice una nueva consulta'}]
            return True, error
        return False, item.cantidad_beneficiarios


'''Subscription'''

'''Credit'''


class Credit(Base):
    __tablename__ = 'credito'

    id_credito = Column(Integer, primary_key=True)
    id_usuario = Column(Integer, ForeignKey('usuario.id_usuario'), nullable=False)
    id_usuario_origen = Column(Integer, ForeignKey('usuario.id_usuario'), nullable=False)
    id_origen_credito = Column(Integer, ForeignKey('origen_credito.id_origen_credito'), nullable=False)
    valor = Column(Float, nullable=False)
    valido_desde = Column(DateTime(timezone=True), nullable=False)
    valido_hasta = Column(DateTime(timezone=True), nullable=False)
    usuario = relationship("User", foreign_keys=[id_usuario])
    usuario_origen = relationship("User", foreign_keys=[id_usuario_origen])
    origen_credito = relationship("CreditOrigin", foreign_keys=[id_origen_credito])


class CreditOrigin(Base):
    __tablename__ = 'origen_credito'

    id_origen_credito = Column(Integer, primary_key=True)
    origen_credito = Column(String, nullable=False)

'''Credit'''
