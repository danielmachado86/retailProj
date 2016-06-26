from sqlalchemy import Column, DateTime, Date, String, Integer, Boolean, ForeignKey, func, and_, UniqueConstraint
from sqlalchemy.orm import relationship
from dbmodel.dbconfig import Base


from functools import partial
partial(Column, nullable=False)


Base.metadata.schema = 'servicio'

class ServiceCancellation(Base):
    # __table_args__ = {'schema': 'servicio'}
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
    # __table_args__ = {'schema': 'servicio'}
    __tablename__ = 'estado_servicio'

    id_estado_servicio = Column(Integer, primary_key=True)
    estado_servicio = Column(String)


class ReasonCancellation(Base):
    # __table_args__ = {'schema': 'servicio'}
    __tablename__ = 'motivo_cancelacion'

    id_motivo_cancelacion = Column(Integer, primary_key=True)
    motivo_cancelacion = Column(String)


class ServiceProvider(Base):
    # __table_args__ = {'schema': 'servicio'}
    __tablename__ = 'prestador_servicio'

    id_prestador_servicio = Column(Integer, primary_key=True)
    id_usuario = Column(
        Integer, ForeignKey('usuario.usuario.id_usuario'))
    id_rol = Column(
        Integer, ForeignKey('rol_prestador_servicio.id_rol'))
    id_tipo_documento = Column(
        Integer, ForeignKey('tipo_documento.id_tipo_documento'))
    numero_movil = Column(String)
    documento_identidad = Column(String)
    fecha_nacimiento = Column(Date)
    direccion_residencia = Column(String)
    telefono_residencia = Column(String)
    usuario = relationship('User', foreign_keys=[id_usuario])
    rol = relationship('ServiceProviderRole', foreign_keys=[id_rol])
    tipo_documento = relationship('IDType', foreign_keys=[id_tipo_documento])


class ServiceProviderSchedule(Base):
    # __table_args__ = {'schema': 'servicio'}
    __tablename__ = 'programacion_prestador_servicio'

    id_programacion_prestador_servicio = Column(Integer, primary_key=True)
    id_prestador_servicio = Column(
        Integer, ForeignKey('prestador_servicio.id_prestador_servicio'))
    id_almacen = Column(
        Integer, ForeignKey('almacen.almacen.id_almacen'))
    id_recurso = Column(
        Integer, ForeignKey('almacen.recurso.id_recurso'))
    desde = Column(DateTime(timezone=True))
    hasta = Column(DateTime(timezone=True))
    prestador_servicio = relationship('ServiceProvider', foreign_keys=[id_prestador_servicio])
    almacen = relationship('Warehouse', foreign_keys=[id_almacen])
    recurso = relationship('Resource', foreign_keys=[id_recurso])


class ServiceProviderRole(Base):
    # __table_args__ = {'schema': 'servicio'}
    __tablename__ = 'rol_prestador_servicio'

    id_rol = Column(Integer, primary_key=True)
    rol = Column(String)


class Service(Base):
    # __table_args__ = {'schema': 'servicio'}
    __tablename__ = 'servicio'

    id_servicio = Column(Integer, primary_key=True)
    id_prestador_servicio = Column(
        Integer, ForeignKey('prestador_servicio.id_prestador_servicio'))
    id_usuario = Column(
        Integer, ForeignKey('usuario.usuario.id_usuario'))
    id_direccion = Column(
        Integer, ForeignKey('usuario.direccion_usuario.id_direccion'))
    id_orden = Column(
        Integer, ForeignKey('orden.orden.id_orden'))
    id_estado_servicio = Column(
        Integer, ForeignKey('estado_servicio.id_estado_servicio'))
    inicio = Column(DateTime(timezone=True))
    fin = Column(DateTime(timezone=True))
    prestador_servicio = relationship('ServiceProvider', foreign_keys=[id_prestador_servicio])
    usuario = relationship('User', foreign_keys=[id_usuario])
    direccion = relationship('UserLocation', foreign_keys=[id_direccion])
    orden = relationship('Order', foreign_keys=[id_orden])
    estado_servicio = relationship('ServiceStatus', foreign_keys=[id_estado_servicio])


class IDType(Base):
    # __table_args__ = {'schema': 'servicio'}
    __tablename__ = 'tipo_documento'

    id_tipo_documento = Column(Integer, primary_key=True)
    tipo_documento = Column(String)
