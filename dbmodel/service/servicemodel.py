import datetime
from geoalchemy2 import Geometry
from sqlalchemy import Column, DateTime, Date, String, Integer, Boolean, ForeignKey, func, and_, UniqueConstraint, or_
from sqlalchemy.orm import relationship
from dbmodel.dbconfig import Base, s


from functools import partial
partial(Column, nullable=False)


Base.metadata.schema = 'servicio'


class ServiceCancellation(Base):
    __tablename__ = 'cancelacion_servicio'

    id_cancelacion_servicio = Column(Integer, primary_key=True)
    id_servicio = Column(
        Integer, ForeignKey('servicio.id_servicio'))
    id_credito = Column(
        Integer, ForeignKey('usuario.credito.id_credito'))
    id_motivo_cancelacion = Column(
        Integer, ForeignKey('motivo_cancelacion.id_motivo_cancelacion'))
    fecha_cancelacion = Column(DateTime(timezone=True))
    servicio = relationship('Service', foreign_keys=[id_servicio])
    credito = relationship('Credit', foreign_keys=[id_credito])
    motivo_cancelacion = relationship('ReasonCancellation', foreign_keys=[id_motivo_cancelacion])


class ServiceStatus(Base):
    __tablename__ = 'estado_servicio'

    id_estado_servicio = Column(Integer, primary_key=True)
    estado_servicio = Column(String)


class ReasonCancellation(Base):
    __tablename__ = 'motivo_cancelacion'

    id_motivo_cancelacion = Column(Integer, primary_key=True)
    motivo_cancelacion = Column(String)


class ServiceProvider(Base):
    __tablename__ = 'prestador_servicio'

    id_prestador_servicio = Column(Integer, primary_key=True)
    id_usuario = Column(Integer, ForeignKey('usuario.usuario.id_usuario'), nullable=False)
    id_rol = Column(Integer, nullable=False)
    id_tipo_documento = Column(Integer, nullable=False)
    documento_identidad = Column(String, nullable=False)
    fecha_nacimiento = Column(Date, nullable=False)
    direccion_residencia = Column(String, nullable=False)
    telefono_residencia = Column(String, nullable=True)
    fecha_creacion = Column(DateTime(timezone=True), nullable=False)
    ultima_ubicacion = Column(Geometry(geometry_type='POINT'), nullable=True)
    usuario = relationship('User', foreign_keys=[id_usuario])

    def get_role(self):
        role = {1: 'Transportador',
                2: 'Coordinador'}
        return role.get(self.id_rol)

    def get_id_type(self):
        id_type = {1: 'Cédula ciudadanía',
                   2: 'Pasaporte',
                   3: 'Cédula extranjería'}
        return id_type.get(self.id_tipo_documento)

    def __init__(self, user, role, id_type, id_number, birthdate, address, phone, last_location):
        self.id_usuario = user
        self.id_rol = role
        self.id_tipo_documento = id_type
        self.documento_identidad = id_number
        self.fecha_nacimiento = birthdate
        self.direccion_residencia = address
        self.telefono_residencia = phone
        self.fecha_creacion = datetime.datetime.now(),
        self.ultima_ubicacion = 'POINT({} {})'.format(last_location[1], last_location[0])

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id_prestador_servicio,
            'usuario': self.usuario.nombre_completo,
            'rol': self.get_role(),
            'cantidad': self.get_id_type(),
            'movil': self.numero_movil,
            'documento': self.documento_identidad,
            'fecha nacimiento': self.fecha_nacimiento.strftime("%Y-%m-%d"),
            'direccion': self.direccion,
            'telefono': self.telefono_residencia,
            'fecha creacion': self.fecha_creacion.strftime("%Y-%m-%d"),
        }

    def add_item(self):
        s.add(self)
        s.commit()
        resp = [201, {'message': 'El proveedor de servicio se añadió exitosamente'}]
        return False, resp

    @staticmethod
    def get_service_provider(wh):
        active_sp = s.query(ServiceProviderSchedule.id_prestador_servicio,
                             func.ST_X(ServiceProvider.ultima_ubicacion),
                             func.ST_Y(ServiceProvider.ultima_ubicacion)).join(ServiceProvider).filter(
            and_(ServiceProviderSchedule.id_almacen == wh,
                 ServiceProviderSchedule.inicio < datetime.datetime.now(),
                 ServiceProviderSchedule.fin > datetime.datetime.now())).all()

        selected_sp = None

        return False, selected_sp


class ServiceProviderSchedule(Base):
    __tablename__ = 'programacion_prestador_servicio'

    id_programacion_prestador_servicio = Column(Integer, primary_key=True)
    id_prestador_servicio = Column(Integer, ForeignKey('prestador_servicio.id_prestador_servicio'), nullable=False)
    id_almacen = Column(Integer, ForeignKey('almacen.almacen.id_almacen'), nullable=False)
    inicio = Column(DateTime(timezone=True), nullable=False)
    fin = Column(DateTime(timezone=True), nullable=False)
    prestador_servicio = relationship('ServiceProvider', foreign_keys=[id_prestador_servicio])
    almacen = relationship('Warehouse', foreign_keys=[id_almacen])

    def __init__(self, service_pvdr, wh, start, end):
        self.id_prestador_servicio = service_pvdr
        self.id_almacen = wh
        self.inicio = start
        self.fin = end

    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        return {
            'id': self.id_programacion_prestador_servicio,
            'prestador servicio': self.prestador_servicio,
            'almacen': self.almacen,
            'inicio': self.inicio.strftime("%Y-%m-%d"),
            'fin': self.fin.strftime("%Y-%m-%d")
        }

    def add_item(self):
        s.add(self)
        s.commit()
        resp = [201, {'message': 'La programación se creó exitosamente'}]
        return False, resp

    @staticmethod
    def get_active_service_provider(wh):
        sp_list = s.query(ServiceProviderSchedule).filter(and_(
            ServiceProviderSchedule.id_almacen == wh,
            ServiceProviderSchedule.inicio < datetime.datetime.now(),
            ServiceProviderSchedule.fin > datetime.datetime.now())).all()
        if not sp_list:
            error = [404, {'message': 'No existen transportadores activos',
                           'action': 'Realice de nuevo la confirmación de la orden'}]
            return True, error
        return False, sp_list


class Service(Base):
    __tablename__ = 'servicio'

    id_servicio = Column(Integer, primary_key=True)
    id_prestador_servicio = Column(Integer, ForeignKey('prestador_servicio.id_prestador_servicio'),  nullable=False)
    id_direccion = Column(Integer, ForeignKey('usuario.direccion_usuario.id_direccion'),  nullable=False)
    id_orden = Column(Integer, ForeignKey('orden.orden.id_orden'),  nullable=False)
    id_estado_servicio = Column(Integer,  nullable=False)
    inicio = Column(DateTime(timezone=True),  nullable=False)
    fin = Column(DateTime(timezone=True),  nullable=True)
    prestador_servicio = relationship('ServiceProvider', foreign_keys=[id_prestador_servicio])
    direccion = relationship('UserLocation', foreign_keys=[id_direccion])
    orden = relationship('Order', foreign_keys=[id_orden])

    def get_service_status(self):
        service_status = {1: 'Pendiente',
                          2: 'En proceso',
                          3: 'En tránsito',
                          4: 'Entregado',
                          5: 'Aceptado',
                          6: 'Cancelado'}
        return service_status.get(self.id_estado_servicio)

    def __init__(self, service_pvdr, location, order, service_status, end_service):
        self.id_prestador_servicio = service_pvdr
        self.id_direccion = location
        self.id_orden = order
        self.id_estado_servicio = service_status
        self.inicio = datetime.datetime.now()
        self.finalizado = end_service

    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        return {
            'id': self.id_servicio,
            'prestador servicio': self.prestador_servicio,
            'direccion': self.direccion,
            'orden': self.id_orden,
            'estado servicio': self.get_service_status(),
            'inicio': self.inicio.strftime("%Y-%m-%d"),
            'fin': self.finalizado.strftime("%Y-%m-%d"),
        }

    def add_item(self):
        s.add(self)
        s.commit()
        resp = [201, {'message': 'El servicio se creó exitosamente'}]
        return False, resp


class Vehicle(Base):
    __tablename__ = 'vehiculo'

    id_vehiculo = Column(Integer, primary_key=True)
    id_prestador_servicio = Column(Integer, ForeignKey('prestador_servicio.id_prestador_servicio'), nullable=False)
    id_tipo_vehiculo = Column(Integer, nullable=False)
    matricula = Column(String, nullable=True)
    descripcion = Column(String, nullable=False)
    prestador_servicio = relationship("ServiceProvider", foreign_keys=[id_prestador_servicio])

    def get_vehicle_type(self):
        vehicle_type = {1: 'Bicicleta',
                        2: 'Motocicleta',
                        3: 'Carro'}
        return vehicle_type.get(self.id_tipo_vehiculo)

    def __init__(self, service_pvdr, vehicle_type, license_plate, description):
        self.id_prestador_servicio = service_pvdr
        self.id_tipo_vehiculo = vehicle_type
        self.matricula = license_plate
        self.descripcion = description

    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        return {
            'id': self.id_vehiculo,
            'prestador servicio': self.prestador_servicio,
            'tipo vehiculo': self.get_vehicle_type(),
            'placa': self.matricula,
            'descripcion': self.descripcion
        }

    def add_item(self):
        s.add(self)
        s.commit()
        resp = [201, {'message': 'El vehículo se creó exitosamente'}]
        return False, resp
