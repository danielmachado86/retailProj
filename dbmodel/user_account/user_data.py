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
from dbmodel.database_model import UserModel, UserLocationModel

from sqlalchemy.ext.hybrid import hybrid_property


class User(UserModel):

    def __init__(self, full_name, email_address, phone_number, password, auth_type_id):
        self.user_id = uuid.uuid4()
        self.full_name = full_name
        self.email_address = email_address
        self.phone_number = phone_number
        self.username = username_generator(self.full_name)
        self.auth_type_id = auth_type_id
        self.password = password
        salt = bcrypt.gensalt(10)
        hashed = bcrypt.hashpw(self.password.encode('utf-8'), salt)
        self.password_hash = hashed.decode('utf-8')
        self.password_salt = salt.decode('utf-8')
        check_user_not_exists_by_id(self.user_id)
        check_user_not_exists_by_mail(self.email_address)
        check_user_not_exists_by_phone(self.phone_number)

    @hybrid_property
    def full_name(self):
        return self._full_name

    @full_name.setter
    def full_name(self, full_name):
        if re.match("[a-zA-Z0-9]+", unidecode(full_name).replace(" ", "")) is None:
            raise InvalidArgument('El campo nombre no puede estar vacio')
        self._full_name = full_name

    @hybrid_property
    def email_address(self):
        return self._email_address

    @email_address.setter
    def email_address(self, email_address):
        if not email_address or '': raise InvalidArgument('El campo mail no puede estar vacio o nulo')
        self._email_address = email_address

    @hybrid_property
    def phone_number(self):
        return self._phone_number

    @phone_number.setter
    def phone_number(self, phone_number):
        if not phone_number or '': raise InvalidArgument('El campo phone no puede estar vacio o nulo')
        self._phone_number = phone_number

    @hybrid_property
    def username(self):
        return self._username

    @username.setter
    def username(self, username):
        if not username or '': raise InvalidArgument('El campo nombre de usuario no puede estar vacio o nulo')
        self._username = username

    @hybrid_property
    def password(self):
        return self._password

    @password.setter
    def password(self, password):
        if password is None or password is '':
            raise InvalidArgument('La contraseña no cuenta con las características requeridas')
        self._password = password

    @hybrid_property
    def auth_type_id(self):
        return self._auth_type_id

    @auth_type_id.setter
    def auth_type_id(self, auth_type_id):
        if not (1 <= int(auth_type_id) <= 3):
            raise InvalidArgument('El tipo de autenticacion debe ser un numero entero desde el 1 hasta el 3')
        self._auth_type_id = auth_type_id


    def __repr__(self):
        return '<Usuario %r>' % self.email_address

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.user_id,
            'nombre': self.full_name,
            'username': self.username
        }

    def verify_password(self, password):
        if self is None:
            return False
        if self.password_hash == bcrypt.hashpw(
                password.encode('utf-8'), self.password_salt.encode('utf-8')
        ).decode("utf-8"):
            return True

    def add_item(self):
        s.add(self)
        s.commit()
        return {'success':True}, 201, {'ContentType':'application/json'}

    def verify_account(self):
        #TODO: IMPLEMENTAR TOKEN. USAR METODO generate_auth_token(self, expiration=600)
        if self.verified: raise ResourceConflict('La cuenta ya se encuentra confirmada')
        self.verified = True
        s.commit()
        return {'success':True}, 200, {'ContentType':'application/json'}

    def update_user_info(self, name, mail, phone):
        self.full_name = name
        if self.email_address != mail:
            check_user_not_exists_by_mail(mail)
            self.email_address = mail
        if self.phone_number != phone:
            check_user_not_exists_by_phone(phone)
            self.phone_number = phone
        s.commit()
        return {'success': True}, 200, {'ContentType': 'application/json'}

    def update_user_name(self, name):
        self.full_name = name
        s.commit()
        return {'success': True}, 200, {'ContentType': 'application/json'}

    def update_username(self, username):
        check_user_not_exists_by_username(username)
        self.username = username
        s.commit()
        return {'success': True}, 200, {'ContentType': 'application/json'}

    def change_user_password(self, password):
        if self.auth_type_id != 1:
            raise InvalidArgument('Su cuenta utiliza un servicio de terceros para autenticación')
        self.password = password
        salt = bcrypt.gensalt(10)
        hashed = bcrypt.hashpw(self.password.encode('utf-8'), salt)
        self.password_hash = hashed.decode('utf-8')
        self.password_salt = salt.decode('utf-8')
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
    if s.query(User).filter(User.username == username).first():
        try:
            return username_generator(name)
        except RecursionError:
            return username_generator(name, size=size + 1)
    return username

def generate_auth_token(user_id, expiration=600):
    secret_key = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(32))
    serial = Serializer(secret_key, expires_in=expiration)
    return serial.dumps({'id': str(user_id)})

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
    if s.query(User).filter(User.user_id == item_id).first():
        raise ResourceConflict('Este user_account id ya se encuentra asociado a una cuenta')

def check_user_not_exists_by_mail(mail):
    if not mail:
        raise InvalidArgument('El campo mail no puede estar vacio o nulo')
    if s.query(User).filter(User.email_address == mail).first():
        raise ResourceConflict('Este correo electronico ya se encuentra asociado a una cuenta')

def check_user_not_exists_by_username(username):
    if not username:
        raise InvalidArgument('El campo username no puede estar vacio o nulo')
    if s.query(User).filter(User.username == username).first():
        raise ResourceConflict('Este nombre de usuario ya se encuentra asociado a una cuenta')

def check_user_not_exists_by_phone(phone):
    if not phone:
        raise InvalidArgument('El campo phone no puede estar vacio o nulo')
    if s.query(User).filter(User.phone_number == phone).first():
        raise ResourceConflict('Este numero de telefono ya se encuentra asociado a una cuenta')

def get_user_by_mail(mail):
    if not mail:
        raise InvalidArgument('El campo mail no puede estar vacio o nulo')
    user = s.query(User).filter(
        User.email_address == mail).first()
    if not user:
        raise ResourceConflict('Este usuario no existe')
    return user

def get_user_by_id(id_user):
    if not id_user:
        raise InvalidArgument('El campo user_account id no puede estar vacio o nulo')
    user = s.query(User).filter(
        User.user_id == id_user).first()
    if not user:
        raise ResourceConflict('Este usuario no existe')
    return user

# class UserImage(UserImageModel):
#
#     def __init__(self, id_usuario, description, url):
#         self.id_usuario = id_usuario
#         self.descripcion = description
#         self.url = url
#
#     @hybrid_property
#     def id_usuario(self):
#         return self._user_id
#
#     @id_usuario.setter
#     def id_usuario(self, id_usuario):
#         if not id_usuario or '':
#             raise InvalidArgument('El campo user_account id no puede estar vacio')
#         self._user_id = id_usuario
#
#     @hybrid_property
#     def url(self):
#         return self._url
#
#     @url.setter
#     def url(self, url):
#         if not url or '':
#             raise InvalidArgument('El campo url no puede estar vacio')
#         self._url = url
#
#     def add_user_image(self):
#         s.add(self)
#         s.commit()
#         return {'success': True}, 201, {'ContentType': 'application/json'}
#
#     def update_user_image(self, description):
#         self.descripcion = description
#         s.commit()
#         return {'success': True}, 200, {'ContentType': 'application/json'}
#
#     def delete_user_image(self):
#         s.delete(self)
#         s.commit()
#         return {'success': True}, 200, {'ContentType': 'application/json'}
#
# def get_user_images_by_user_id(id_user):
#     if not id_user:
#         raise InvalidArgument('El campo user_account id no puede estar vacio o nulo')
#     return s.query(UserImage).filter(
#         UserImage.id_usuario == id_user).all()

class UserLocation(UserLocationModel):

    _location = None

    def __init__(self, user_id, city_id, user_address_name, location, address, address_reference, is_favorite = False, is_active = True):
        self.user_id = user_id
        self.city_id = city_id
        self.user_address_name = user_address_name
        self.location = location
        self.gps = 'POINT({} {})'.format(self.location[0], self.location[1])
        self.address = address
        self.address_reference = address_reference
        self.is_favorite = is_favorite
        self.is_active = is_active

    @hybrid_property
    def user_id(self):
        return self._user_id

    @user_id.setter
    def user_id(self, user_id):
        if not user_id or '':
            raise InvalidArgument('El campo user_account id no puede estar vacio')
        self._user_id = user_id

    @hybrid_property
    def city_id(self):
        return self._city_id

    @city_id.setter
    def city_id(self, city_id):
        if not city_id or '':
            raise InvalidArgument('El campo id ciudad usuario no puede estar vacio')
        self._city_id = city_id

    @hybrid_property
    def user_address_name(self):
        return self._user_address_name

    @user_address_name.setter
    def user_address_name(self, user_address_name):
        if not user_address_name or '':
            raise InvalidArgument('El campo nombre address no puede estar vacio')
        self._user_address_name = user_address_name

    @hybrid_property
    def location(self):
        return self._location

    @location.setter
    def location(self, location):
        if not location or '':
            raise InvalidArgument('El campo gps no puede estar vacio')
        self._location = location

    @hybrid_property
    def address(self):
        return self._address

    @address.setter
    def address(self, address):
        if not address or '':
            raise InvalidArgument('El campo address no puede estar vacio')
        self._address = address

    @hybrid_property
    def fecha_registro(self):
        return self._fecha_registro

    @fecha_registro.setter
    def fecha_registro(self, fecha_registro):
        if not fecha_registro or '':
            raise InvalidArgument('El campo fecha registro no puede estar vacio')
        self._fecha_registro = fecha_registro

    @hybrid_property
    def is_favorite(self):
        return self._is_favorite

    @is_favorite.setter
    def is_favorite(self, is_favorite):
        self._is_favorite = is_favorite

    @hybrid_property
    def is_active(self):
        return self._is_active

    @is_active.setter
    def is_active(self, is_active):
        self._is_active = is_active

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'user_address_id': self.user_address_id,
            'nombre': self.user_address_name,
            'gps': self.gps,
            'address': self.address,
            'address_reference': self.address_reference,
            'fecha': self.fecha_registro.strftime("%Y-%m-%d"),
            'favorite': self._is_favorite
        }

    def add_location(self):
        s.add(self)
        s.commit()
        return {'success': True}, 200, {'ContentType': 'application/json'}


def get_address_list_by_user(id_user):
    if not id_user or '':
        raise InvalidArgument('El campo id_user no puede estar vacio')
    return s.query(UserLocation).filter(
        UserLocation.user_id == id_user).all()

def get_address_list_by_user_location(id_user, location):
    if not id_user or '':
        raise InvalidArgument('El campo id_user no puede estar vacio')
    if not location or '':
        raise InvalidArgument('El campo location no puede estar vacio')
    addresses = s.query(UserLocation,
                        UserLocation.gps.ST_Distance_Sphere(
                            'POINT({} {})'.format(location[0], location[1])
                        )).filter(
        and_(UserLocation.gps.ST_Distance_Sphere(
            'POINT({} {})'.format(location[0], location[1])
        )<= 1000, UserLocation.user_id == id_user))
    return addresses

def get_address_by_id(item_id):
    location_item = s.query(UserLocation,
                             func.ST_X(UserLocation.gps),
                             func.ST_Y(UserLocation.gps),
                             func.ST_AsText(UserLocation.gps)
                             ).filter(UserLocation.user_address_id == item_id).first()
    return location_item