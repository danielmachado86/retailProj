import datetime
from pytz import timezone
import pytz

from geoalchemy2.shape import to_shape
from sqlalchemy import and_, func, text
from dbmodel.dbconfig import s
import uuid
from sqlalchemy.orm import relationship

from dbmodel.res.custom_exceptions import InvalidArgument, ResourceConflict
from dbmodel.database_model import StoreModel, StoreLocationModel, EmployeeRequestStatusModel,\
    StoreEmployeeModel, StoreHoursModel, StoreEmployeeRoleModel

from sqlalchemy.ext.hybrid import hybrid_property

class Store(StoreModel):

    StoreModel.store_location = relationship("StoreLocation", back_populates="store", uselist=False)

    def __init__(self, store_category_id, store_name, store_address, latitude, longitude, city_id, store_phone):
        self.store_id = uuid.uuid4()
        self.store_category_id = store_category_id
        self.store_name = store_name
        self.store_phone = store_phone
        self.store_date = datetime.datetime.now()
        self.store_location = StoreLocation(self.store_id, store_address, latitude, longitude, city_id)

    @hybrid_property
    def store_category_id(self):
        return self._store_category_id

    @store_category_id.setter
    def store_category_id(self, store_category_id):
        if not store_category_id or '':
            raise InvalidArgument('El campo id_categoria_almacen no puede estar vacio')
        self._store_category_id = store_category_id

    @hybrid_property
    def store_name(self):
        return self._store_name

    @store_name.setter
    def store_name(self, store_name):
        if not store_name or '':
            raise InvalidArgument('El campo nombre almacen no puede estar vacio')
        self._store_name = store_name

    @hybrid_property
    def store_phone(self):
        return self._store_phone

    @store_phone.setter
    def store_phone(self, store_phone):
        if not store_phone or '':
            raise InvalidArgument('El campo contacto no puede estar vacio')
        self._store_phone = store_phone

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id_almacen': self.store_id,

            'nombre': self.store_name,
            'url': 'http://localhost:5000/v1.0/tienda/{}'.format(self.store_id),
        }

    def add_item(self):
        s.add(self)
        s.commit()
        return {'success': True}, 200, {'ContentType': 'application/json'}

def get_warehouse_by_id(warehouse_id):
    if not warehouse_id or '':
        raise InvalidArgument('El campo warehouse_id no puede estar vacio')
    warehouse = s.query(Store).filter(
        Store.store_id == warehouse_id).first()
    return warehouse

def get_warehouse_by_location(location):
    if not location or '':
        raise InvalidArgument('El campo location no puede estar vacio')
    warehouses = s.query(Store, StoreLocation.store_gps.ST_Distance_Sphere(
                            'POINT({} {})'.format(location[0], location[1])
                        )).join(StoreLocation).filter(StoreLocation.store_gps.ST_Distance_Sphere(
            'POINT({} {})'.format(location[0], location[1])
        ) <= 2000)
    whs = []
    for wh in warehouses:
        wh[0].distancia = wh[1]
        whs.append(wh[0])
    print('Almacenes dentro de rango =>', [(wh.store_name, wh.distancia) for wh in whs])
    return whs

def check_warehouse_not_exists_by_name(name):
    if not name or '':
        raise InvalidArgument('El campo name no puede estar vacio')
    if s.query(Store).filter(
            Store.store_name == name).first():
        raise ResourceConflict('Este nombre de tienda ya se encuentra en uso')

def get_warehouse_by_name(name):
    if not name or '':
        raise InvalidArgument('El campo name no puede estar vacio')
    warehouse = s.query(Store).filter(
        Store.store_name == name).first()
    return warehouse


class StoreLocation(StoreLocationModel):

    _latitude = None
    _longitude = None
    StoreLocationModel.store = relationship("Store", back_populates="store_location", uselist=False)

    def __init__(self, store_id, store_address, latitude, longitude, city_id):
        self.store_id = store_id
        self.store_address = store_address
        self.latitude = latitude
        self.longitude = longitude
        self.location = [self.latitude, self.longitude]
        self.store_gps = 'POINT({} {})'.format(self.location[0], self.location[1])
        self.city_id = city_id

    @hybrid_property
    def store_id(self):
        return self._store_id

    @store_id.setter
    def store_id(self, store_id):
        if not store_id or '':
            raise InvalidArgument('El campo id_almacen no puede estar vacio')
        self._store_id = store_id

    @hybrid_property
    def store_address(self):
        return self._store_address

    @store_address.setter
    def store_address(self, store_address):
        if not store_address or '':
            raise InvalidArgument('El campo address no puede estar vacio')
        self._store_address = store_address

    @hybrid_property
    def city_id(self):
        return self._city_id

    @city_id.setter
    def city_id(self, city_id):
        if not city_id or '':
            raise InvalidArgument('El campo id ciudad usuario no puede estar vacio')
        self._city_id = city_id

    @hybrid_property
    def latitude(self):
        return self._latitude

    @latitude.setter
    def latitude(self, latitude):
        if not latitude or '':
            raise InvalidArgument('El campo latitud no puede estar vacio')
        self._latitude = latitude

    @hybrid_property
    def longitude(self):
        return self._longitude

    @longitude.setter
    def longitude(self, longitude):
        if not longitude or '':
            raise InvalidArgument('El campo latitud no puede estar vacio')
        self._longitude = longitude

    def add_item(self):
        s.add(self)
        s.commit()


class StoreEmployee(StoreEmployeeModel):

    def __init__(self, id_user, id_warehouse):
        self.user_id = id_user
        self.store_id = id_warehouse


    @hybrid_property
    def user_id(self):
        return self._user_id

    @user_id.setter
    def user_id(self, user_id):
        if not user_id or '':
            raise InvalidArgument('El campo id_usuario no puede estar vacio')
        self._user_id = user_id

    @hybrid_property
    def store_id(self):
        return self._store_id

    @store_id.setter
    def store_id(self, store_id):
        if not store_id or '':
            raise InvalidArgument('El campo id_almacen no puede estar vacio')
        self._store_id = store_id

    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        return {
            'id_miembro': self.store_employee_id,
        }

    def add_warehouse_member(self, requested_by):
        s.add(self)
        s.commit()
        update_warehouse_member_status(self.store_employee_id, 1, requested_by)
        update_warehouse_member_role(self.store_employee_id, 2, requested_by)
        return {'success': True}, 200, {'ContentType': 'application/json'}

def get_warehouse_members(id_warehouse):
    if not id_warehouse or '':
        raise InvalidArgument('El campo id_warehouse no puede estar vacio')
    return s.query(StoreEmployee).filter(
        StoreEmployee.store_id == id_warehouse)

def get_user_warehouse_memberships(id_user):
    if not id_user or '':
        raise InvalidArgument('El campo id_user no puede estar vacio')
    return s.query(StoreEmployee).filter(
        StoreEmployee.user_id == id_user)


class EmployeeRequestStatus(EmployeeRequestStatusModel):

    def __init__(self, store_employee_id, request_status, requested_by):
        self.store_employee_id = store_employee_id
        self.request_status = request_status
        self.requested_by = requested_by
        self.request_date = datetime.datetime.now()

    @hybrid_property
    def store_employee_id(self):
        return self._store_employee_id

    @store_employee_id.setter
    def store_employee_id(self, store_employee_id):
        if not store_employee_id or '':
            raise InvalidArgument('El campo id_miembro_almacen no puede estar vacio')
        self._store_employee_id = store_employee_id

    @hybrid_property
    def request_status(self):
        return self._request_status

    @request_status.setter
    def request_status(self, request_status):
        if not request_status or '':
            raise InvalidArgument('El campo estado_solicitud no puede estar vacio')
        self._request_status = request_status

    @hybrid_property
    def requested_by(self):
        return self._requested_by

    @requested_by.setter
    def requested_by(self, requested_by):
        if not requested_by or '':
            raise InvalidArgument('El campo id_actualizado_por no puede estar vacio')
        self._requested_by = requested_by

    def get_request_status(self):
        estado_solicitud = {1: 'Enviada',
                            2: 'Aceptada',
                            3: 'Rechazada',
                            4: 'Bloqueada'}
        return estado_solicitud.get(self.request_status)

def update_warehouse_member_status(id_miembro_almacen, status, updated_by):
    member_status = EmployeeRequestStatus(id_miembro_almacen, status, updated_by)
    historia = member_status
    s.add(historia)
    s.commit()
    return {'success': True}, 200, {'ContentType': 'application/json'}

class StoreEmployeeRole(StoreEmployeeRoleModel):

    def __init__(self, store_employee_id, store_employee_role, requested_by):
        self.store_employee_id = store_employee_id
        self.store_employee_role = store_employee_role
        self.requested_by = requested_by
        self.request_date = datetime.datetime.now()

    @hybrid_property
    def store_employee_id(self):
        return self._store_employee_id

    @store_employee_id.setter
    def store_employee_id(self, store_employee_id):
        if not store_employee_id or '':
            raise InvalidArgument('El campo id_miembro_almacen no puede estar vacio')
        self._store_employee_id = store_employee_id

    @hybrid_property
    def store_employee_role(self):
        return self._store_employee_role

    @store_employee_role.setter
    def store_employee_role(self, store_employee_role):
        if not store_employee_role or '':
            raise InvalidArgument('El campo estado_solicitud no puede estar vacio')
        self._store_employee_role = store_employee_role

    @hybrid_property
    def requested_by(self):
        return self._requested_by

    @requested_by.setter
    def requested_by(self, requested_by):
        if not requested_by or '':
            raise InvalidArgument('El campo id_actualizado_por no puede estar vacio')
        self._requested_by = requested_by

    def get_role(self):
        rol = { 1: 'Administrador',
                2: 'Operario'}
        return rol.get(self.store_employee_role)

def update_warehouse_member_role(id_miembro_almacen, role, updated_by):
    member_role = StoreEmployeeRole(id_miembro_almacen, role, updated_by)
    rol = member_role
    s.add(rol)
    s.commit()
    return {'success': True}, 200, {'ContentType': 'application/json'}


class StoreHours(StoreHoursModel):

    def __init__(self, store_id, day, open_hh, open_mm, close_hh, close_mm):
        self.store_id = store_id
        self.day = day
        self.store_open = datetime.time(open_hh, open_mm)
        self.store_close = datetime.time(close_hh, close_mm)

    @hybrid_property
    def store_id(self):
        return self._store_id

    @store_id.setter
    def store_id(self, store_id):
        if not store_id or '':
            raise InvalidArgument('El campo id_almacen no puede estar vacio')
        self._store_id = store_id

    @hybrid_property
    def day(self):
        return self._day

    @day.setter
    def day(self, day):
        if not day or '':
            raise InvalidArgument('El campo dia no puede estar vacio')
        if not (1 <= int(day) <= 8):
            raise InvalidArgument('Este campo debe ser un numero entero desde el 1 hasta el 8')
        self._day = day

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.store_id,
            'dia': self.get_day(),
            'abre': str(self.store_open),
            'cierra': str(self.store_close)
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
        return rol.get(self.day)

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
    if s.query(StoreHours).filter(and_(
            StoreHours.store_id == warehouse, StoreHours.day == day)).first():
        raise ResourceConflict('Este horario ya se encuentra asociado al almacen')
    return {'success': True}, 200, {'ContentType': 'application/json'}

if __name__ == '__main__':
    from dbmodel.database_init import drop_database, create_database
    drop_database()