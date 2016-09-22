import datetime

from sqlalchemy import Column, DateTime, Date, String, Integer, Boolean, ForeignKey, and_, UniqueConstraint, func, text
from sqlalchemy.orm import relationship, backref
from dbmodel.dbconfig import Base, s, engine
from geoalchemy2.types import Geometry

Base.metadata.schema = 'almacen'


class Warehouse(Base):
    __tablename__ = 'almacen'

    id_almacen = Column(Integer, primary_key=True)
    id_categoria_almacen = Column(Integer, ForeignKey('categoria_almacen.id_categoria_almacen'), nullable=False)
    id_ciudad_almacen = Column(Integer, ForeignKey('ciudad_almacen.id_ciudad_almacen'), nullable=False)
    nombre = Column(String, nullable=False, unique=True, index=True)
    coordenadas = Column(Geometry(geometry_type='POINT'), nullable=False)
    direccion = Column(String, nullable=False)
    telefono = Column(String, nullable=False)
    celular = Column(String, nullable=False)
    fecha_creacion = Column(DateTime(timezone=True), nullable=False)
    categoria_almacen = relationship("Category", foreign_keys=[id_categoria_almacen])
    ciudad_almacen = relationship("WarehouseCity", foreign_keys=[id_ciudad_almacen])
    distancia = float('infinity')

    horario = relationship('WarehouseOpeningHours', primaryjoin="Warehouse.id_almacen==WarehouseOpeningHours.id_almacen",
                           backref=backref('almacen', uselist=False), cascade="all, delete-orphan", lazy='subquery')

    miembro = relationship('WarehouseMember', primaryjoin="Warehouse.id_almacen==WarehouseMember.id_almacen",
                             backref=backref('almacen', uselist=False), cascade="all, delete-orphan", lazy='subquery')

    @classmethod
    def create(cls, wh, category, city, name, location, address, phone, mobile, created, distance):
        obj = cls()
        obj.id_almacen = wh
        obj.id_categoria_almacen = category
        obj.id_ciudad_almacen = city
        obj.nombre = name
        obj.coordenadas = location
        obj.direccion = address
        obj.telefono = phone
        obj.celular = mobile
        obj.fecha_creacion = created
        obj.distancia = distance
        return obj

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        horario = self.horario
        miembro = self.miembro
        return {
            'id_almacen': self.id_almacen,
            'categoria': self.categoria_almacen.categoria_almacen,
            'ciudad': self.ciudad_almacen.ciudad,
            'pais': self.ciudad_almacen.pais_almacen.nombre_pais,
            'nombre': self.nombre,
            'coordenadas': self.coordenadas,
            'direccion': self.direccion,
            'telefono': self.telefono,
            'movil': self.celular,
            'url': 'http://localhost:5000/v1.0/tienda/{}'.format(self.id_almacen),
            'horario': self.make_list(horario),
            'miembros': self.make_list(miembro),
            'distancia': self.distancia
        }

    @staticmethod
    def make_list(item_list):
        final_list = []
        for item in item_list:
            final_list.append(item.serialize)
        return final_list

    @staticmethod
    def get_item(item_id):
        warehouse_item = s.query(Warehouse,
                                 func.ST_X(Warehouse.coordenadas),
                                 func.ST_Y(Warehouse.coordenadas),
                                 func.ST_AsText(Warehouse.coordenadas)
                                 ).filter(Warehouse.id_almacen == item_id).first()
        warehouse_item[0].coordenadas = '{}, {}'.format(warehouse_item[1], warehouse_item[2])
        warehouse_item = warehouse_item[0]
        if not warehouse_item:
            warehouse_error = [404, {'message': 'Esta relación no existe',
                                     'action': 'Realice una nueva consulta'}]
            return True, warehouse_error
        return False, warehouse_item

    @staticmethod
    def get_warehouse_by_location(location):

        sql = text("SELECT *, ST_Distance_Sphere(almacen.almacen.coordenadas, ST_PointFromText('"
                   + 'POINT({} {})'.format(location[1], location[0]) + "'))"
                   "AS almacen_almacen_id_almacen "
                   "FROM almacen.almacen "
                   "WHERE ST_Distance_Sphere(almacen.almacen.coordenadas, ST_PointFromText('"
                   + 'POINT({} {})'.format(location[1], location[0]) + "')) <= 7000")

        result = engine.execute(sql)
        whs = []
        for row in result:
            whs.append(Warehouse.create(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9]))
        return whs

    @staticmethod
    def check_item_exists_by_name(name):
        if not name:
            mssg = [400, {'message': 'El campo name no puede ser vacio o nulo',
                          'action': 'Ingrese un valor adecuado'}]
            return True, mssg
        if not isinstance(name, str):
            mssg = [400, {'message': 'El valor del campo name debe ser una cadena de texto',
                          'action': 'Ingrese un valor adecuado'}]
            return True, mssg
        if s.query(Warehouse).filter(
                        Warehouse.nombre == name).first():
            mssg = [409, {'message': 'Este almacen existe'}]
            return True, mssg
        mssg = [200, {'message': 'Este almacen no existe'}]
        return False, mssg

    @staticmethod
    def get_item_by_name(name):
        if not name:
            mssg = [400, {'message': 'El campo name no puede ser vacio o nulo',
                          'action': 'Ingrese un valor adecuado'}]
            return True, mssg
        if not isinstance(name, str):
            mssg = [400, {'message': 'El valor del campo name debe ser una cadena de texto',
                          'action': 'Ingrese un valor adecuado'}]
            return True, mssg
        item = s.query(Warehouse).filter(
            Warehouse.nombre == name).first()
        if not item:
            mssg = [404, {'message': 'Este grupo no existe',
                           'action': 'Realice una nueva consulta'}]
            return True, mssg
        return False, item

    @staticmethod
    def get_item_by_id(item_id):
        if not isinstance(item_id, int):
            return None
        return s.query(Warehouse).filter(
            Warehouse.id_almacen == item_id).first()

    def add_item(self, category, city, name, location, address, phone, mobile, user):
        if not isinstance(category, int):
            mssg = [400, {'message': 'El campo category debe ser un numero entero',
                          'action': 'Ingrese un valor adecuado'}]
            return True, mssg
        if not isinstance(city, int):
            mssg = [400, {'message': 'El campo city debe ser un numero entero',
                          'action': 'Ingrese un valor adecuado'}]
            return True, mssg
        if not name:
            mssg = [400, {'message': 'El campo name no puede ser vacio o nulo',
                          'action': 'Ingrese un valor adecuado'}]
            return True, mssg
        error, resp = self.check_item_exists_by_name(name)
        if error:
            mssg = [409, {'message': 'Esta tienda existe'}]
            return True, mssg
        if not isinstance(location, list):
            mssg = [400, {'message': 'El campo location debe ser una lista que contiene lat y lon',
                          'action': 'Ingrese un valor adecuado'}]
            return True, mssg
        if not isinstance(location[0], float):
            mssg = [400, {'message': 'El campo lat debe ser tipo float',
                          'action': 'Ingrese un valor adecuado'}]
            return True, mssg
        if not isinstance(location[1], float):
            mssg = [400, {'message': 'El campo lon debe ser tipo float',
                          'action': 'Ingrese un valor adecuado'}]
            return True, mssg
        if not address:
            mssg = [400, {'message': 'El campo address no puede ser vacio o nulo',
                          'action': 'Ingrese un valor adecuado'}]
            return True, mssg
        if not phone:
            mssg = [400, {'message': 'El campo phone no puede ser vacio o nulo',
                          'action': 'Ingrese un valor adecuado'}]
            return True, mssg
        if not mobile:
            mssg = [400, {'message': 'El campo mobile no puede ser vacio o nulo',
                          'action': 'Ingrese un valor adecuado'}]
            return True, mssg
        self.id_categoria_almacen = category
        self.id_ciudad_almacen = city
        self.nombre = name
        self.coordenadas = 'POINT({} {})'.format(location[1], location[0])
        self.direccion = address
        self.telefono = phone
        self.celular = mobile
        self.fecha_creacion = datetime.datetime.now()
        s.add(self)
        s.flush()
        WarehouseMember.create(self.id_almacen, 1, user)
        s.commit()
        resp = [201, {'message': 'La tienda se ha creado exitosamente'}]
        return False, resp


class Category(Base):
    __tablename__ = 'categoria_almacen'

    id_categoria_almacen = Column(Integer, primary_key=True)
    categoria_almacen = Column(String, nullable=False)


class WarehouseMemberHistory(Base):
    __tablename__ = 'historia_miembro_almacen'

    id_historia_miembro_almacen = Column(Integer, primary_key=True)
    id_miembro_almacen = Column(Integer, ForeignKey('miembro_almacen.id_miembro_almacen'), nullable=False)
    # id_estado_solicitud = Column(Integer, ForeignKey('usuario.estado_solicitud.id_estado_solicitud'), nullable=False)
    id_estado_solicitud = Column(Integer, nullable=False)
    id_actualizado_por = Column(Integer, ForeignKey('miembro_almacen.id_miembro_almacen'), nullable=False)
    # miembro_almacen = relationship("WarehouseMember", foreign_keys=[id_miembro_almacen])

    actualizado_por = relationship("WarehouseMember", foreign_keys=[id_actualizado_por])

    def __init__(self, member, state, updated_by):
        self.id_miembro_almacen = member
        self.id_estado_solicitud = state
        self.id_actualizado_por = updated_by

    def get_request_status(self):
        estado_solicitud = {1: 'Enviada',
                            2: 'Aprobada',
                            3: 'Negada',
                            4: 'Bloqueada'}
        return estado_solicitud.get(self.id_estado_solicitud)


class WarehouseMember(Base):
    __tablename__ = 'miembro_almacen'

    id_miembro_almacen = Column(Integer, primary_key=True)
    id_usuario = Column(Integer, ForeignKey('usuario.usuario.id_usuario'), index=True, nullable=False)
    id_almacen = Column(Integer, ForeignKey('almacen.id_almacen'), index=True, nullable=False)
    id_rol_miembro_almacen = Column(Integer, ForeignKey('rol_miembro_almacen.id_rol_miembro_almacen'), nullable=False)
    usuario = relationship("User", foreign_keys=[id_usuario])
    rol_miembro_almacen = relationship("MemberRole", foreign_keys=[id_rol_miembro_almacen])

    __table_args__ = (UniqueConstraint('id_usuario', 'id_almacen', name='miembro_unico'),)

    historia = relationship(
        'WarehouseMemberHistory',
        primaryjoin="WarehouseMember.id_miembro_almacen==WarehouseMemberHistory.id_miembro_almacen",
        backref=backref('miembro_almacen', uselist=False),
        cascade="all, delete-orphan", lazy='subquery'
    )

    @classmethod
    def create(cls, warehouse, role, user):
        obj = cls()
        obj.id_usuario = user
        obj.id_almacen = warehouse
        obj.id_rol_miembro_almacen = role
        s.add(obj)
        s.flush()

        s.add(WarehouseMemberHistory(obj.id_miembro_almacen, 2, obj.id_miembro_almacen))
        return obj

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id_miembro': self.id_miembro_almacen,
            'usuario': self.usuario.nombre_completo,
            'rol': self.rol_miembro_almacen.rol_miembro_almacen,
            'estado': self.historia[0].get_request_status()
        }

    @staticmethod
    def check_item_exists_by_warehouse_user(warehouse, user):
        if s.query(WarehouseOpeningHours).filter(and_(
                        WarehouseMember.id_almacen == warehouse, WarehouseMember.user == user)).first():
            mssg = [409, {'message': 'Este miembro existe'}]
            return True, mssg
        mssg = [200, {'message': 'Este miembro no existe'}]
        return False, mssg

    def add_item(self, user, warehouse, role, updated_by):
        if not isinstance(user, int):
            mssg = [400, {'message': 'El campo user debe ser un numero entero',
                          'action': 'Ingrese un valor adecuado'}]
            return True, mssg
        if not isinstance(warehouse, int):
            mssg = [400, {'message': 'El campo warehouse debe ser un numero entero',
                          'action': 'Ingrese un valor adecuado'}]
            return True, mssg
        if not (1 <= int(role) <= 3):
            error = [400, {'message': 'Error en los parámetros suministrados',
                           'action': 'Los valores aceptados son: 1:Creador, 2:Admin, 3:Participante'}]
            return True, error
        error, mssg = self.check_item_exists_by_warehouse_user(warehouse, user)
        if error:
            return True, mssg
        self.id_usuario = user
        self.id_almacen = warehouse
        self.id_rol_miembro_almacen = role
        s.add(self)
        s.flush()
        s.add(WarehouseMemberHistory(self.id_miembro_almacen, 1, updated_by))
        s.commit()
        resp = [201, {'message': 'El miembro se ha creado exitosamente'}]
        return False, resp


class MemberRole(Base):
    __tablename__ = 'rol_miembro_almacen'

    id_rol_miembro_almacen = Column(Integer, primary_key=True)
    rol_miembro_almacen = Column(String, nullable=False)


class WarehouseCity(Base):
    __tablename__ = 'ciudad_almacen'

    id_ciudad_almacen = Column(Integer, primary_key=True)
    id_pais_almacen = Column(Integer, ForeignKey('pais_almacen.id_pais_almacen'), nullable=False)
    ciudad = Column(String, nullable=False)
    codigo_ciudad_iso = Column(String, nullable=False)
    pais_almacen = relationship("WarehouseCountry", foreign_keys=[id_pais_almacen])


class WarehouseCountry(Base):
    __tablename__ = 'pais_almacen'

    id_pais_almacen = Column(Integer, primary_key=True)
    id_continente_almacen = Column(Integer, ForeignKey('continente_almacen.id_continente_almacen'), nullable=False)
    locale = Column(String, nullable=False)
    codigo_pais_iso = Column(String, nullable=False)
    nombre_pais = Column(String, nullable=False)
    continente_almacen = relationship("WarehouseContinent", foreign_keys=[id_continente_almacen])


class WarehouseContinent(Base):
    __tablename__ = 'continente_almacen'

    id_continente_almacen = Column(Integer, primary_key=True)
    codigo_continente = Column(String, nullable=False)
    nombre_continente = Column(String, nullable=False)
    locale = Column(String, nullable=False)


class WarehouseOpeningHours(Base):
    __tablename__ = 'horario_atencion'

    id_horario_atencion = Column(Integer, primary_key=True)
    id_almacen = Column(Integer, ForeignKey('almacen.id_almacen'), nullable=False)
    dia = Column(Integer, nullable=False)
    desde_hora = Column(Integer, nullable=False)
    desde_minutos = Column(Integer, nullable=False)
    hasta_hora = Column(Integer, nullable=False)
    hasta_minutos = Column(Integer, nullable=False)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id_almacen,
            'dia': self.dia,
            'abre': str(self.desde_hora) + ' ' + str(self.desde_minutos),
            'cierra': str(self.hasta_hora) + ' ' + str(self.hasta_minutos)
        }

    @staticmethod
    def check_item_exists_by_warehouse_day(warehouse, day):
        if s.query(WarehouseOpeningHours).filter(and_(
                        WarehouseOpeningHours.id_almacen == warehouse, WarehouseOpeningHours.dia == day)).first():
            mssg = [409, {'message': 'Este horario existe'}]
            return True, mssg
        mssg = [200, {'message': 'Este horario no existe'}]
        return False, mssg

    def add_item(self, warehouse, day, from_hour, from_minutes, until_hour, until_minutes):
        if not isinstance(warehouse, int):
            mssg = [400, {'message': 'El campo warehouse debe ser un numero entero',
                          'action': 'Ingrese un valor adecuado'}]
            return True, mssg
        if not (1 <= int(day) <= 7):
            mssg = [400, {'message': 'Error en los parámetros suministrados',
                          'action': 'Los valores aceptados son: 1: Lunes, 2: Martes, 3: Miercoles ...'}]
            return True, mssg
        if not (0 <= int(from_hour) <= 23):
            mssg = [400, {'message': 'Error en los parámetros suministrados',
                          'action': 'El rango de valores 0-23'}]
            return True, mssg
        if not (0 <= int(from_minutes) <= 59):
            mssg = [400, {'message': 'Error en los parámetros suministrados',
                          'action': 'El rango de valores 0-59'}]
            return True, mssg
        if not (0 <= int(until_hour) <= 23):
            mssg = [400, {'message': 'Error en los parámetros suministrados',
                          'action': 'El rango de valores 0-23'}]
            return True, mssg
        if not (0 <= int(until_minutes) <= 59):
            mssg = [400, {'message': 'Error en los parámetros suministrados',
                          'action': 'El rango de valores 0-59'}]
            return True, mssg
        error, mssg = self.check_item_exists_by_warehouse_day(warehouse, day)
        if error:
            return True, mssg

        self.id_almacen = warehouse
        self.dia = day
        self.desde_hora = from_hour
        self.desde_minutos = from_minutes
        self.hasta_hora = until_hour
        self.hasta_minutos = until_minutes
        s.add(self)
        s.commit()
        resp = [201, {'message': 'El horario se ha creado exitosamente'}]
        return False, resp
