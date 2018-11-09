import re
import datetime
from unidecode import unidecode
import bcrypt
from sqlalchemy import  func, and_
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired
import random
import string
import uuid
from dbmodel.dbconfig import s
from dbmodel.res.custom_exceptions import *
from dbmodel.database_model import UserModel, UserImageModel, UserLocationModel

from sqlalchemy.ext.hybrid import hybrid_property


class User(UserModel):

    def __init__(self, nombre_completo, correo_electronico, numero_movil, contrasena, id_tipo_autenticacion):
        self.id_usuario = uuid.uuid4()
        self.nombre_completo = nombre_completo
        self.correo_electronico = correo_electronico
        self.numero_movil = numero_movil
        self.nombre_usuario = username_generator(self.nombre_completo)
        self.id_tipo_autenticacion = id_tipo_autenticacion
        self.contrasena = contrasena
        salt = bcrypt.gensalt(10)
        hashed = bcrypt.hashpw(self.contrasena.encode('utf-8'), salt)
        self.contrasena_hash = hashed.decode('utf-8')
        self.contrasena_salt = salt.decode('utf-8')
        check_user_not_exists_by_id(self.id_usuario)
        check_user_not_exists_by_mail(self._correo_electronico)
        check_user_not_exists_by_phone(self._numero_movil)

    @hybrid_property
    def nombre_completo(self):
        return self._nombre_completo

    @nombre_completo.setter
    def nombre_completo(self, nombre_completo):
        if re.match("[a-zA-Z0-9]+", unidecode(nombre_completo).replace(" ", "")) is None:
            raise InvalidArgument('El campo nombre no puede estar vacio')
        self._nombre_completo = nombre_completo

    @hybrid_property
    def correo_electronico(self):
        return self._correo_electronico

    @correo_electronico.setter
    def correo_electronico(self, correo_electronico):
        if not correo_electronico or '': raise InvalidArgument('El campo mail no puede estar vacio o nulo')
        self._correo_electronico = correo_electronico

    @hybrid_property
    def numero_movil(self):
        return self._numero_movil

    @numero_movil.setter
    def numero_movil(self, numero_movil):
        if not numero_movil or '': raise InvalidArgument('El campo phone no puede estar vacio o nulo')
        self._numero_movil = numero_movil

    @hybrid_property
    def nombre_usuario(self):
        return self._nombre_usuario

    @nombre_usuario.setter
    def nombre_usuario(self, nombre_usuario):
        if not nombre_usuario or '': raise InvalidArgument('El campo nombre de usuario no puede estar vacio o nulo')
        self._nombre_usuario = nombre_usuario

    @hybrid_property
    def contrasena(self):
        return self._contrasena

    @contrasena.setter
    def contrasena(self, contrasena):
        if contrasena is None or contrasena is '':
            raise InvalidArgument('La contraseña no cuenta con las características requeridas')
        self._contrasena = contrasena

    @hybrid_property
    def id_tipo_autenticacion(self):
        return self._id_tipo_autenticacion

    @id_tipo_autenticacion.setter
    def id_tipo_autenticacion(self, id_tipo_autenticacion):
        if not (1 <= int(id_tipo_autenticacion) <= 3):
            raise InvalidArgument('El tipo de autenticacion debe ser un numero entero desde el 1 hasta el 3')
        self._id_tipo_autenticacion =id_tipo_autenticacion


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

    def verify_password(self, password):
        if self is None:
            return False
        if self.contrasena_hash == bcrypt.hashpw(
                password.encode('utf-8'), self.contrasena_salt.encode('utf-8')
        ).decode("utf-8"):
            return True

    def add_item(self):
        s.add(self)
        s.commit()
        return {'success':True}, 201, {'ContentType':'application/json'}

    def verify_account(self):
        #TODO: IMPLEMENTAR TOKEN. USAR METODO generate_auth_token(self, expiration=600)
        if self.verificado: raise ResourceConflict('La cuenta ya se encuentra confirmada')
        self.verificado = True
        s.commit()
        return {'success':True}, 200, {'ContentType':'application/json'}

    def update_user_info(self, name, mail, phone):
        self.nombre_completo = name
        if self.correo_electronico != mail:
            check_user_not_exists_by_mail(mail)
            self.correo_electronico = mail
        if self.numero_movil != phone:
            check_user_not_exists_by_phone(phone)
            self.numero_movil = phone
        s.commit()
        return {'success': True}, 200, {'ContentType': 'application/json'}

    def update_user_name(self, name):
        self.nombre_completo = name
        s.commit()
        return {'success': True}, 200, {'ContentType': 'application/json'}

    def update_username(self, username):
        check_user_not_exists_by_username(username)
        self.nombre_usuario = username
        s.commit()
        return {'success': True}, 200, {'ContentType': 'application/json'}

    def change_user_password(self, password):
        if self.id_tipo_autenticacion != 1:
            raise InvalidArgument('Su cuenta utiliza un servicio de terceros para autenticación')
        self.contrasena = password
        salt = bcrypt.gensalt(10)
        hashed = bcrypt.hashpw(self.contrasena.encode('utf-8'), salt)
        self.contrasena_hash = hashed.decode('utf-8')
        self.contrasena_salt = salt.decode('utf-8')
        s.commit()
        return {'success': True}, 200, {'ContentType': 'application/json'}

def username_generator(name, size=6, chars=string.digits):
    if re.match("[a-zA-Z0-9]+", unidecode(name).replace(" ", "")) is None:
        raise InvalidArgument('El campo name debe tener al menos una letra o numero')
    name = unidecode(name).lower()
    nameproc = name.split(" ")
    if nameproc.__len__() >= 2:
        name = nameproc[0] + '-' + nameproc[1]
    elif nameproc.__len__() == 1:
        name = nameproc[0]
    else:
        name = 'retailproj'
    username = name + "-" + ''.join(random.choice(chars) for _ in range(size))
    if s.query(User).filter(User.nombre_usuario == username).first():
        try:
            return username_generator(name)
        except RecursionError:
            return username_generator(name, size=size + 1)
    return username

def generate_auth_token(id_usuario, expiration=600):
    secret_key = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(32))
    serial = Serializer(secret_key, expires_in=expiration)
    return serial.dumps({'id': str(id_usuario)})

def verify_auth_token(token):
    secret_key = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(32))
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

def check_user_not_exists_by_id(item_id):
    if not item_id:
        raise InvalidArgument('El campo item_id no puede ser vacio o nulo')
    if s.query(User).filter(User.id_usuario == item_id).first():
        raise ResourceConflict('Este user id ya se encuentra asociado a una cuenta')

def check_user_not_exists_by_mail(mail):
    if not mail:
        raise InvalidArgument('El campo mail no puede estar vacio o nulo')
    if s.query(User).filter(User.correo_electronico == mail).first():
        raise ResourceConflict('Este correo electronico ya se encuentra asociado a una cuenta')

def check_user_not_exists_by_username(username):
    if not username:
        raise InvalidArgument('El campo username no puede estar vacio o nulo')
    if s.query(User).filter(User.nombre_usuario == username).first():
        raise ResourceConflict('Este nombre de usuario ya se encuentra asociado a una cuenta')

def check_user_not_exists_by_phone(phone):
    if not phone:
        raise InvalidArgument('El campo phone no puede estar vacio o nulo')
    if s.query(User).filter(User.numero_movil == phone).first():
        raise ResourceConflict('Este numero de telefono ya se encuentra asociado a una cuenta')

def get_user_by_mail(mail):
    if not mail:
        raise InvalidArgument('El campo mail no puede estar vacio o nulo')
    user = s.query(User).filter(
        User.correo_electronico == mail).first()
    if not user:
        raise ResourceConflict('Este usuario no existe')
    return user

def get_user_by_id(id_user):
    if not id_user:
        raise InvalidArgument('El campo user id no puede estar vacio o nulo')
    user = s.query(User).filter(
        User.id_usuario == id_user).first()
    if not user:
        raise ResourceConflict('Este usuario no existe')
    return user

class UserImage(UserImageModel):

    def __init__(self, id_usuario, description, url):
        self.id_usuario = id_usuario
        self.descripcion = description
        self.url = url

    @hybrid_property
    def id_usuario(self):
        return self._id_usuario

    @id_usuario.setter
    def id_usuario(self, id_usuario):
        if not id_usuario or '':
            raise InvalidArgument('El campo user id no puede estar vacio')
        self._id_usuario = id_usuario

    @hybrid_property
    def url(self):
        return self._url

    @url.setter
    def url(self, url):
        if not url or '':
            raise InvalidArgument('El campo url no puede estar vacio')
        self._url = url

    def add_user_image(self):
        s.add(self)
        s.commit()
        return {'success': True}, 201, {'ContentType': 'application/json'}

    def update_user_image(self, description):
        self.descripcion = description
        s.commit()
        return {'success': True}, 200, {'ContentType': 'application/json'}

    def delete_user_image(self):
        s.delete(self)
        s.commit()
        return {'success': True}, 200, {'ContentType': 'application/json'}

def get_user_images_by_user_id(id_user):
    if not id_user:
        raise InvalidArgument('El campo user id no puede estar vacio o nulo')
    return s.query(UserImage).filter(
        UserImage.id_usuario == id_user).all()

class UserLocation(UserLocationModel):

    _location = None

    def __init__(self, id_usuario, id_ciudad, nombre_direccion, location, address, reference):
        self.id_usuario = id_usuario
        self.id_ciudad = id_ciudad
        self.nombre_direccion = nombre_direccion
        self.location = location
        self.coordenadas = 'POINT({} {})'.format(self.location[0], self.location[1])
        self.direccion = address
        self.referencia = reference
        self.fecha_registro = datetime.datetime.now()
        self.favorito = False

    @hybrid_property
    def id_usuario(self):
        return self._id_usuario

    @id_usuario.setter
    def id_usuario(self, id_usuario):
        if not id_usuario or '':
            raise InvalidArgument('El campo user id no puede estar vacio')
        self._id_usuario = id_usuario

    @hybrid_property
    def id_ciudad(self):
        return self._id_ciudad

    @id_ciudad.setter
    def id_ciudad(self, id_ciudad):
        if not id_ciudad or '':
            raise InvalidArgument('El campo id ciudad usuario no puede estar vacio')
        self._id_ciudad = id_ciudad

    @hybrid_property
    def nombre_direccion(self):
        return self._nombre_direccion

    @nombre_direccion.setter
    def nombre_direccion(self, nombre_direccion):
        if not nombre_direccion or '':
            raise InvalidArgument('El campo nombre direccion no puede estar vacio')
        self._nombre_direccion = nombre_direccion

    @hybrid_property
    def location(self):
        return self._location

    @location.setter
    def location(self, location):
        if not location or '':
            raise InvalidArgument('El campo coordenadas no puede estar vacio')
        self._location = location

    @hybrid_property
    def direccion(self):
        return self._direccion

    @direccion.setter
    def direccion(self, direccion):
        if not direccion or '':
            raise InvalidArgument('El campo direccion no puede estar vacio')
        self._direccion = direccion

    @hybrid_property
    def fecha_registro(self):
        return self._fecha_registro

    @fecha_registro.setter
    def fecha_registro(self, fecha_registro):
        if not fecha_registro or '':
            raise InvalidArgument('El campo fecha registro no puede estar vacio')
        self._fecha_registro = fecha_registro

    @hybrid_property
    def favorito(self):
        return self._favorito

    @favorito.setter
    def favorito(self, favorito):
        self._favorito = favorito

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id_direccion': self.id_direccion,
            'usuario': self.usuario._nombre_completo,
            'ciudad': self.ciudad.ciudad,
            'pais': self.ciudad.pais.nombre_pais,
            'continente': self.ciudad.pais.continente.nombre_continente,
            'nombre': self.nombre_direccion,
            'coordenadas': self.coordenadas,
            'direccion': self.direccion,
            'referencia': self.referencia,
            'fecha': self.fecha_registro.strftime("%Y-%m-%d"),
            'favorito': self.favorito
        }

    def add_location(self):
        s.add(self)
        s.commit()
        return {'success': True}, 200, {'ContentType': 'application/json'}


def get_address_list_by_user(id_user):
    if not id_user or '':
        raise InvalidArgument('El campo id_user no puede estar vacio')
    return s.query(UserLocation).filter(
        UserLocation.id_usuario == id_user).all()

def get_address_list_by_user_location(id_user, location):
    if not id_user or '':
        raise InvalidArgument('El campo id_user no puede estar vacio')
    if not location or '':
        raise InvalidArgument('El campo location no puede estar vacio')
    addresses = s.query(UserLocation,
                        UserLocation.coordenadas.ST_Distance_Sphere(
                            'POINT({} {})'.format(location[0], location[1])
                        )).filter(
        and_(UserLocation.coordenadas.ST_Distance_Sphere(
            'POINT({} {})'.format(location[0], location[1])
        )<= 1000, UserLocation.id_usuario == id_user))
    return addresses

def get_address_by_id(item_id):
    location_item = s.query(UserLocation,
                             func.ST_X(UserLocation.coordenadas),
                             func.ST_Y(UserLocation.coordenadas),
                             func.ST_AsText(UserLocation.coordenadas)
                             ).filter(UserLocation.id_direccion == item_id).first()
    return location_item


if __name__ == '__main__':
    from dbmodel.database_init import drop_database, create_database
    # create_database()
    #
    # try:
    #     new_user = User('', 'danielmcis@hotmail.com', '673046628054', 'Freqm0d+', 1)
    #     new_user.add_item()
    # except InvalidArgument as e:
    #     print(e.to_dict(), e.status_code)
    #
    # try:
    #     new_user = User('Daniel Machado', '', '6730466280540', 'Freqm0d+', 1)
    #     new_user.add_item()
    # except InvalidArgument as e:
    #     print(e.to_dict(), e.status_code)
    #
    # try:
    #     new_user = User('Daniel Machado', 'danielmcis0@hotmail.com', '', 'Freqm0d+', 1)
    #     new_user.add_item()
    # except InvalidArgument as e:
    #     print(e.to_dict(), e.status_code)
    #
    #
    # try:
    #     new_user = User('Daniel Machado', 'danielmcis01@hotmail.com', '6730466280540', '', 1)
    #     new_user.add_item()
    # except InvalidArgument as e:
    #     print(e.to_dict(), e.status_code)
    #
    # try:
    #     new_user = User('Daniel Machado', 'danielmcis02@hotmail.com', '67304662805402', 'Freqm0d+', 4)
    #     new_user.add_item()
    # except InvalidArgument as e:
    #     print(e.to_dict(), e.status_code)
    #
    # try:
    #     new_user = User('Daniel Machado', 'danielmcis1@hotmail.com', '6730466280541', 'Freqm0d+', 1)
    #     new_user.add_item()
    #     user_1 = get_user_by_id(new_user.id_usuario)
    #     print(user_1)
    # except InvalidArgument as e:
    #     print(e.to_dict(), e.status_code)
    #
    # try:
    #     new_user = User('Daniel Machado', 'danielmcis2@hotmail.com', '6730466280542', 'Freqm0d+', 1)
    #     new_user.add_item()
    #     check_user_not_exists_by_id(new_user.id_usuario)
    # except InvalidArgument as e:
    #     print(e.to_dict(), e.status_code)
    #
    # try:
    #     new_user = User('Daniel Machado', 'danielmcis3@hotmail.com', '6730466280543', 'Freqm0d+', 1)
    #     new_user.add_item()
    #     check_user_not_exists_by_mail(new_user.correo_electronico)
    # except InvalidArgument as e:
    #     print(e.to_dict(), e.status_code)
    #
    # try:
    #     new_user = User('Daniel Machado', 'danielmcis4@hotmail.com', '6730466280544', 'Freqm0d+', 1)
    #     new_user.add_item()
    #     check_user_not_exists_by_username(new_user.nombre_usuario)
    # except InvalidArgument as e:
    #     print(e.to_dict(), e.status_code)
    #
    # try:
    #     new_user = User('Daniel Machado', 'danielmcis5@hotmail.com', '6730466280545', 'Freqm0d+', 1)
    #     new_user.add_item()
    #     check_user_not_exists_by_phone(new_user.numero_movil)
    # except InvalidArgument as e:
    #     print(e.to_dict(), e.status_code)
    #
    # try:
    #     new_user = User('Daniel Machado', 'danielmcis6@hotmail.com', '6730466280546', 'Freqm0d+', 1)
    #     new_user.add_item()
    #     user_1 = get_user_by_mail(new_user.correo_electronico)
    #     print(user_1)
    # except InvalidArgument as e:
    #     print(e.to_dict(), e.status_code)
    #
    # try:
    #     new_user = User('Daniel Machado', 'danielmcis7@hotmail.com', '6730466280547', 'Freqm0d+', 1)
    #     new_user.add_item()
    #     new_image = UserImage(new_user.id_usuario, 'Descripcion', 'URL')
    #     new_image.add_user_image()
    #     print(new_image)
    # except InvalidArgument as e:
    #     print(e.to_dict(), e.status_code)
    #
    # try:
    #     new_user = User('Daniel Machado', 'danielmcis8@hotmail.com', '6730466280548', 'Freqm0d+', 1)
    #     new_user.add_item()
    #     new_image = UserImage(new_user.id_usuario, 'Descripcion', 'URL')
    #     new_image.add_user_image()
    #     images = get_user_images_by_user_id(new_user.id_usuario)
    #     print(images)
    #     new_image = UserImage(new_user.id_usuario, 'Descripcion', '')
    #     new_image.add_user_image()
    # except InvalidArgument as e:
    #     print(e.to_dict(), e.status_code)
    #
    # try:
    #     new_user = User('Daniel Machado', 'danielmcis9@hotmail.com', '6730466280549', 'Freqm0d+', 1)
    #     new_user.add_item()
    #     user_1 = get_user_by_id(new_user.id_usuario)
    #     user_1.update_user_info('', 'pepito_perez@domain.com', '55555555')
    # except InvalidArgument as e:
    #     print(e.to_dict(), e.status_code)
    # error, resp = UserLocation().add_item(new_user.id_usuario, 1, 'Casa', [4.650408, -74.059802], 'Calle 73 # 7-51', 'CCB')

    # error, resp = change_user_name(user1_1.id_usuario, 'Pepito Perez')
    # print(error, resp)
    # error, resp = change_username(user1_1.id_usuario, 'Pepito_Perez123456')
    # print(error, resp)
    # error, resp = change_user_password(user1_1.id_usuario, 'micontrasena')
    # print(error, resp)
    drop_database()