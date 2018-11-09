import datetime
from pytz import timezone
import pytz

from geoalchemy2.shape import to_shape
from sqlalchemy import and_, func, text
from dbmodel.dbconfig import s
import uuid
from sqlalchemy.orm import relationship

from dbmodel.res.custom_exceptions import InvalidArgument, ResourceConflict
from dbmodel.database_model import WarehouseModel, WarehouseLocationModel, WarehouseMemberStatusModel,\
    WarehouseMemberModel, WarehouseOpeningHoursModel, WarehouseMemberRoleModel

from sqlalchemy.ext.hybrid import hybrid_property

class Warehouse(WarehouseModel):

    distancia = None
    WarehouseModel.ubicacion = relationship("WarehouseLocation", back_populates="almacen", uselist=False)

    def __init__(self, id_categoria_almacen, nombre, direccion, latitud, longitud, ciudad, contacto):
        self.id_almacen = uuid.uuid4()
        self.id_categoria_almacen = id_categoria_almacen
        self.nombre = nombre
        self.fecha_creacion = datetime.datetime.now()
        self.ubicacion = WarehouseLocation(self.id_almacen, direccion, latitud, longitud, ciudad, contacto)

    @hybrid_property
    def id_categoria_almacen(self):
        return self._id_categoria_almacen

    @id_categoria_almacen.setter
    def id_categoria_almacen(self, id_categoria_almacen):
        if not id_categoria_almacen or '':
            raise InvalidArgument('El campo id_categoria_almacen no puede estar vacio')
        self._id_categoria_almacen = id_categoria_almacen

    @hybrid_property
    def nombre(self):
        return self._nombre

    @nombre.setter
    def nombre(self, nombre):
        if not nombre or '':
            raise InvalidArgument('El campo nombre almacen no puede estar vacio')
        self._nombre = nombre

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id_almacen': self.id_almacen,

            'nombre': self.nombre,
            'url': 'http://localhost:5000/v1.0/tienda/{}'.format(self.id_almacen),
            'distancia': self.distancia
        }

    def add_item(self):
        s.add(self)
        s.commit()
        return {'success': True}, 200, {'ContentType': 'application/json'}

def make_list(item_list):
    final_list = []
    for item in item_list:
        final_list.append(item.serialize)
    return final_list

def get_warehouse_by_id(warehouse_id):
    if not warehouse_id or '':
        raise InvalidArgument('El campo warehouse_id no puede estar vacio')
    warehouse = s.query(Warehouse).filter(
        Warehouse.id_almacen == warehouse_id).first()
    return warehouse

def get_warehouse_by_location(location):
    if not location or '':
        raise InvalidArgument('El campo location no puede estar vacio')
    warehouses = s.query(Warehouse, WarehouseLocation.coordenadas.ST_Distance_Sphere(
                            'POINT({} {})'.format(location[0], location[1])
                        )).join(WarehouseLocation).filter(WarehouseLocation.coordenadas.ST_Distance_Sphere(
            'POINT({} {})'.format(location[0], location[1])
        ) <= 2000)
    whs = []
    for wh in warehouses:
        wh[0].distancia = wh[1]
        whs.append(wh[0])
    print('Almacenes dentro de rango =>', [(wh.nombre, wh.distancia) for wh in whs])
    return whs

def check_warehouse_not_exists_by_name(name):
    if not name or '':
        raise InvalidArgument('El campo name no puede estar vacio')
    if s.query(Warehouse).filter(
                    Warehouse.nombre == name).first():
        raise ResourceConflict('Este nombre de tienda ya se encuentra en uso')

def get_warehouse_by_name(name):
    if not name or '':
        raise InvalidArgument('El campo name no puede estar vacio')
    warehouse = s.query(Warehouse).filter(
        Warehouse.nombre == name).first()
    return warehouse


class WarehouseLocation(WarehouseLocationModel):

    _latitud = None
    _longitud = None
    WarehouseLocationModel.almacen = relationship("Warehouse", back_populates="ubicacion", uselist=False)

    def __init__(self, id_almacen, direccion, latitud, longitud, ciudad, contacto):
        self.id_almacen = id_almacen
        self.direccion = direccion
        self.latitud = latitud
        self.longitud = longitud
        self.location = [self.latitud, self.longitud]
        self.coordenadas = 'POINT({} {})'.format(self.location[0], self.location[1])
        self.id_ciudad = ciudad
        self.contacto = contacto

    @hybrid_property
    def id_almacen(self):
        return self._id_almacen

    @id_almacen.setter
    def id_almacen(self, id_almacen):
        if not id_almacen or '':
            raise InvalidArgument('El campo id_almacen no puede estar vacio')
        self._id_almacen = id_almacen

    @hybrid_property
    def direccion(self):
        return self._direccion

    @direccion.setter
    def direccion(self, direccion):
        if not direccion or '':
            raise InvalidArgument('El campo direccion no puede estar vacio')
        self._direccion = direccion

    @hybrid_property
    def id_ciudad(self):
        return self._id_ciudad

    @id_ciudad.setter
    def id_ciudad(self, id_ciudad):
        if not id_ciudad or '':
            raise InvalidArgument('El campo id ciudad usuario no puede estar vacio')
        self._id_ciudad = id_ciudad

    @hybrid_property
    def latitud(self):
        return self._latitud

    @latitud.setter
    def latitud(self, latitud):
        if not latitud or '':
            raise InvalidArgument('El campo latitud no puede estar vacio')
        self._latitud = latitud

    @hybrid_property
    def longitud(self):
        return self._longitud

    @longitud.setter
    def longitud(self, longitud):
        if not longitud or '':
            raise InvalidArgument('El campo latitud no puede estar vacio')
        self._longitud = longitud

    @hybrid_property
    def contacto(self):
        return self._contacto

    @contacto.setter
    def contacto(self, contacto):
        if not contacto or '':
            raise InvalidArgument('El campo contacto no puede estar vacio')
        self._contacto = contacto

    def add_item(self):
        s.add(self)
        s.commit()


class WarehouseMember(WarehouseMemberModel):

    def __init__(self, id_user, id_warehouse, id_updated_by):
        self.id_usuario = id_user
        self.id_almacen = id_warehouse
        self. id_updated_by = id_updated_by


    @hybrid_property
    def id_usuario(self):
        return self._id_usuario

    @id_usuario.setter
    def id_usuario(self, id_usuario):
        if not id_usuario or '':
            raise InvalidArgument('El campo id_usuario no puede estar vacio')
        self._id_usuario = id_usuario

    @hybrid_property
    def id_almacen(self):
        return self._id_almacen

    @id_almacen.setter
    def id_almacen(self, id_almacen):
        if not id_almacen or '':
            raise InvalidArgument('El campo id_almacen no puede estar vacio')
        self._id_almacen = id_almacen

    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        return {
            'id_miembro': self.id_miembro_almacen,
            'usuario': self.usuario.nombre_completo,
            'rol': self.rol[-1].get_role(),
            'estado': self.status[-1].get_request_status()
        }

    def add_warehouse_member(self):
        s.add(self)
        s.commit()
        update_warehouse_member_status(self.id_miembro_almacen, 1, self.id_updated_by)
        update_warehouse_member_role(self.id_miembro_almacen, 2, self.id_updated_by)
        return {'success': True}, 200, {'ContentType': 'application/json'}

def get_warehouse_members(id_warehouse):
    if not id_warehouse or '':
        raise InvalidArgument('El campo id_warehouse no puede estar vacio')
    return s.query(WarehouseMember).filter(
        WarehouseMember.id_almacen == id_warehouse)

def get_user_warehouse_memberships(id_user):
    if not id_user or '':
        raise InvalidArgument('El campo id_user no puede estar vacio')
    return s.query(WarehouseMember).filter(
        WarehouseMember.id_usuario == id_user)


class WarehouseMemberStatus(WarehouseMemberStatusModel):

    def __init__(self, member, status, updated_by):
        self.id_miembro_almacen = member
        self.estado_solicitud = status
        self.id_actualizado_por = updated_by
        self.fecha_modificacion = datetime.datetime.now()

    @hybrid_property
    def id_miembro_almacen(self):
        return self._id_miembro_almacen

    @id_miembro_almacen.setter
    def id_miembro_almacen(self, id_miembro_almacen):
        if not id_miembro_almacen or '':
            raise InvalidArgument('El campo id_miembro_almacen no puede estar vacio')
        self._id_miembro_almacen = id_miembro_almacen

    @hybrid_property
    def estado_solicitud(self):
        return self._estado_solicitud

    @estado_solicitud.setter
    def estado_solicitud(self, estado_solicitud):
        if not estado_solicitud or '':
            raise InvalidArgument('El campo estado_solicitud no puede estar vacio')
        self._estado_solicitud = estado_solicitud

    @hybrid_property
    def id_actualizado_por(self):
        return self._id_actualizado_por

    @id_actualizado_por.setter
    def id_actualizado_por(self, id_actualizado_por):
        if not id_actualizado_por or '':
            raise InvalidArgument('El campo id_actualizado_por no puede estar vacio')
        self._id_actualizado_por = id_actualizado_por

    def get_request_status(self):
        estado_solicitud = {1: 'Enviada',
                            2: 'Aceptada',
                            3: 'Rechazada',
                            4: 'Bloqueada'}
        return estado_solicitud.get(self.estado_solicitud)

def update_warehouse_member_status(id_miembro_almacen, status, updated_by):
    member_status = WarehouseMemberStatus(id_miembro_almacen, status, updated_by)
    historia = member_status
    s.add(historia)
    s.commit()
    return {'success': True}, 200, {'ContentType': 'application/json'}

class WarehouseMemberRole(WarehouseMemberRoleModel):

    def __init__(self, member, role, updated_by):
        self.id_miembro_almacen = member
        self.rol_miembro_almacen = role
        self.id_actualizado_por = updated_by
        self.fecha_modificacion = datetime.datetime.now()

    @hybrid_property
    def id_miembro_almacen(self):
        return self._id_miembro_almacen

    @id_miembro_almacen.setter
    def id_miembro_almacen(self, id_miembro_almacen):
        if not id_miembro_almacen or '':
            raise InvalidArgument('El campo id_miembro_almacen no puede estar vacio')
        self._id_miembro_almacen = id_miembro_almacen

    @hybrid_property
    def rol_miembro_almacen(self):
        return self._rol_miembro_almacen

    @rol_miembro_almacen.setter
    def rol_miembro_almacen(self, rol_miembro_almacen):
        if not rol_miembro_almacen or '':
            raise InvalidArgument('El campo estado_solicitud no puede estar vacio')
        self._rol_miembro_almacen = rol_miembro_almacen

    @hybrid_property
    def id_actualizado_por(self):
        return self._id_actualizado_por

    @id_actualizado_por.setter
    def id_actualizado_por(self, id_actualizado_por):
        if not id_actualizado_por or '':
            raise InvalidArgument('El campo id_actualizado_por no puede estar vacio')
        self._id_actualizado_por = id_actualizado_por

    def get_role(self):
        rol = { 1: 'Administrador',
                2: 'Operario'}
        return rol.get(self.rol_miembro_almacen)

def update_warehouse_member_role(id_miembro_almacen, role, updated_by):
    member_role = WarehouseMemberRole(id_miembro_almacen, role, updated_by)
    rol = member_role
    s.add(rol)
    s.commit()
    return {'success': True}, 200, {'ContentType': 'application/json'}


class WarehouseOpeningHours(WarehouseOpeningHoursModel):

    def __init__(self, warehouse, day, from_h, from_m, to_h, to_m):
        self.id_almacen = warehouse
        self.dia = day
        self.desde = datetime.time(from_h, from_m)
        self.hasta = datetime.time(to_h, to_m)

    @hybrid_property
    def id_almacen(self):
        return self._id_almacen

    @id_almacen.setter
    def id_almacen(self, id_almacen):
        if not id_almacen or '':
            raise InvalidArgument('El campo id_almacen no puede estar vacio')
        self._id_almacen = id_almacen

    @hybrid_property
    def dia(self):
        return self._dia

    @dia.setter
    def dia(self, dia):
        if not dia or '':
            raise InvalidArgument('El campo dia no puede estar vacio')
        if not (1 <= int(dia) <= 8):
            raise InvalidArgument('Este campo debe ser un numero entero desde el 1 hasta el 8')
        self._dia = dia

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id_almacen,
            'dia': self.get_day(),
            'abre': str(self.desde),
            'cierra': str(self.hasta)
        }
    def get_day(self):
        rol = { 1: 'Lunes',
                2: 'Martes',
                3: 'Miercoles',
                4: 'Jueves',
                5: 'Vienes',
                6: 'Sabado',
                7: 'Domingo',
                8: 'Festivo'}
        return rol.get(self.dia)

    def add_warehouse_schedule(self):
        # if not isinstance(warehouse, int):
        #     mssg = [400, {'message': 'El campo warehouse debe ser un numero entero',
        #                   'action': 'Ingrese un valor adecuado'}]
        #     return True, mssg
        # if not (1 <= int(day) <= 7):
        #     mssg = [400, {'message': 'Error en los parámetros suministrados',
        #                   'action': 'Los valores aceptados son: 1: Lunes, 2: Martes, 3: Miercoles ...'}]
        #     return True, mssg
        # if not (0 <= int(from_hour) <= 23):
        #     mssg = [400, {'message': 'Error en los parámetros suministrados',
        #                   'action': 'El rango de valores 0-23'}]
        #     return True, mssg
        # if not (0 <= int(from_minutes) <= 59):
        #     mssg = [400, {'message': 'Error en los parámetros suministrados',
        #                   'action': 'El rango de valores 0-59'}]
        #     return True, mssg
        # if not (0 <= int(until_hour) <= 23):
        #     mssg = [400, {'message': 'Error en los parámetros suministrados',
        #                   'action': 'El rango de valores 0-23'}]
        #     return True, mssg
        # if not (0 <= int(until_minutes) <= 59):
        #     mssg = [400, {'message': 'Error en los parámetros suministrados',
        #                   'action': 'El rango de valores 0-59'}]
        #     return True, mssg
        s.add(self)
        s.commit()
        return {'success': True}, 200, {'ContentType': 'application/json'}


def check_schedule_exists_by_warehouse(warehouse, day):
    if not warehouse:
        raise InvalidArgument('El campo warehouse no puede estar vacio o nulo')
    if not day:
        raise InvalidArgument('El campo day no puede estar vacio o nulo')
    if s.query(WarehouseOpeningHours).filter(and_(
                    WarehouseOpeningHours.id_almacen == warehouse, WarehouseOpeningHours.dia == day)).first():
        raise ResourceConflict('Este horario ya se encuentra asociado al almacen')
    return {'success': True}, 200, {'ContentType': 'application/json'}

if __name__ == '__main__':
    from dbmodel.database_init import drop_database, create_database
    drop_database()