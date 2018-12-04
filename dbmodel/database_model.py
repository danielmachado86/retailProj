from geoalchemy2 import Geometry
from sqlalchemy import Column, DateTime, String, Integer, Boolean, ForeignKey, UniqueConstraint, Float, Date, Time

import datetime

from dbmodel.dbconfig import Base
from dbmodel.res.UUID import GUID

class UserModel(Base):
    __tablename__ = 'user_account'

    user_id = Column(GUID, primary_key=True, autoincrement=False)
    _auth_type_id = Column(Integer, nullable=False)
    _full_name = Column(String, nullable=False)
    _email_address = Column(String, unique=True, index=True, nullable=False)
    _phone_number = Column(String, unique=True, index=True, nullable=False)
    _username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=True)
    password_salt = Column(String, nullable=True)
    verified = Column(Boolean, default=False, nullable=False)


class UserLocationModel(Base):
    __tablename__ = 'user_address'

    user_address_id = Column(Integer, primary_key=True)
    _user_id = Column(GUID, ForeignKey('user_account.user_id'), index=True, nullable=False)
    _city_id = Column(Integer, ForeignKey('city.city_id'), nullable=False)
    _user_address_name = Column(String, nullable=True)
    gps = Column(Geometry(geometry_type='POINT'), nullable=False)
    _address = Column(String, nullable=False)
    address_reference = Column(String, nullable=True)
    _is_favorite = Column(Boolean, nullable=False)
    _is_active = Column(Boolean, nullable=False)


class CountryModel(Base):
    __tablename__ = 'country'

    country_id = Column(Integer, primary_key=True)
    country_locale = Column(String, nullable=False)
    continent_id = Column(Integer, ForeignKey('continent.continent_id'), nullable=False)
    country_iso_code = Column(String, nullable=False)
    country_name = Column(String, nullable=False)


class ContinentModel(Base):
    __tablename__ = 'continent'

    continent_id = Column(Integer, primary_key=True)
    continent_code = Column(String, nullable=False)
    continent_name = Column(String, nullable=False)
    continent_locale = Column(String, nullable=False)


class CityModel(Base):
    __tablename__ = 'city'

    city_id = Column(Integer, primary_key=True)
    country_id = Column(Integer, ForeignKey('country.country_id'), nullable=False)
    city_name = Column(String, nullable=False)
    city_iso_code = Column(String, nullable=False)


class ProductOrderModel(Base):
    __tablename__ = 'product_order'

    product_order_id = Column(Integer, primary_key=True)
    user_id = Column(
        GUID, ForeignKey('user_account.user_id'))
    product_order_date = Column(DateTime(timezone=True))
    is_cancelled = Column(Boolean, nullable=True)


class ProductOrderItemModel(Base):
    __tablename__ = 'product_order_item'

    product_order_item_id = Column(Integer, primary_key=True)
    product_order_id = Column(Integer, ForeignKey('product_order.product_order_id'), nullable=False)
    store_stock_item_id = Column(Integer, ForeignKey('stock_item.stock_item_id'), nullable=False)
    product_order_item_quantity = Column(Integer, nullable=False)
    product_order_item_price = Column(Integer, nullable=False)


class ProductOrderItemErrorModel(Base):
    __tablename__ = 'product_order_error'

    product_order_error_id = Column(Integer, primary_key=True)
    product_order_id = Column(Integer, ForeignKey('product_order.product_order_id'), nullable=False)
    store_stock_item_id = Column(Integer, ForeignKey('product.product_id'), nullable=False)
    product_order_error_quantity = Column(Integer, nullable=False)


class ProductTransactionModel(Base):
    __tablename__ = 'product_order_transaction'

    product_order_transaction_id = Column(Integer, primary_key=True)
    product_order_id = Column(
        Integer, ForeignKey('product_order.product_order_id'))
    payment_method_id = Column(Integer, nullable=False)
    transaction_currency = Column(String, nullable=False)
    transaction_amount = Column(Integer, nullable=False)
    transaction_status_id = Column(Integer, nullable=False)
    payment_reference = Column(String)
    transaction_date = Column(DateTime(timezone=True))


class StockModel(Base):
    __tablename__ = 'stock_item'

    stock_item_id = Column(Integer, primary_key=True)
    product_id = Column(
        Integer, ForeignKey('product.product_id'), nullable=False, index=True)
    store_id = Column(
        GUID, ForeignKey('store.store_id'), nullable=False)
    stock_price = Column(Float, nullable=False)
    product_sku = Column(String, nullable=True)

    __table_args__ = (UniqueConstraint('product_id', 'store_id', name='product_store'),)

class StockInputModel(Base):
    __tablename__ = 'stock_input'

    stock_input_id = Column(Integer, primary_key=True)
    stock_item_id = Column(
        Integer, ForeignKey('stock_item.stock_item_id'), nullable=False, index=True)
    store_member_id = Column(
        Integer, ForeignKey('store_employee.store_employee_id'), nullable=False)
    stock_input_quantity = Column(Integer, nullable=False)
    stock_input_date = Column(DateTime, nullable=False)
    stock_expiration_date = Column(DateTime, nullable=False)


class StockOutputModel(Base):
    __tablename__ = 'stock_output'

    stock_output_id = Column(Integer, primary_key=True)
    stock_item_id = Column(
        Integer, ForeignKey('stock_item.stock_item_id'), nullable=False, index=True)
    store_member_id = Column(
        Integer, ForeignKey('store_employee.store_employee_id'), nullable=False)
    stock_output_quantity = Column(Integer, nullable=False)
    stock_output_reason = Column(Integer, nullable=False)
    stock_output_date = Column(DateTime, nullable=False)


class ProductModel(Base):
    __tablename__ = 'product'

    product_id = Column(Integer, primary_key=True)
    product_category_id = Column(
        Integer, ForeignKey('product_category.product_category_id'), nullable=False, index=True)
    brand_id = Column(
        Integer, ForeignKey('brand.brand_id'), nullable=True, index=True)
    product_name = Column(String, index=True, nullable=False)
    product_unit_measure = Column(Integer, nullable=False)
    product_upc = Column(String, index=True, unique=True, nullable=True)
    product_is_taxable = Column(Boolean, nullable=True)


class ProductCategoryModel(Base):
    __tablename__ = 'product_category'

    product_category_id = Column(Integer, primary_key=True)
    product_category_parent = Column(
        Integer, ForeignKey('product_category.product_category_id'), nullable=True)
    product_category_name = Column(String, nullable=False, unique=True)


class ProductSpecification(Base):
    __tablename__ = 'product_specification'

    product_specification_id = Column(Integer, primary_key=True)
    product_id = Column(
        Integer, ForeignKey('product.product_id'), nullable=False)
    product_attribute = Column(String, nullable=False)
    product_attribute_value = Column(String, nullable=False)


class BrandModel(Base):
    __tablename__ = 'brand'

    brand_id = Column(Integer, primary_key=True)
    brand_name = Column(String, unique=True, nullable=False, index=True)
    brand_description = Column(String, nullable=True)


class BrandImage(Base):
    __tablename__ = 'brand_image'

    brand_image_id = Column(Integer, primary_key=True)
    brand_id = Column(
        Integer, ForeignKey('brand.brand_id'), nullable=False)
    brand_image_description = Column(String, nullable=False)
    brand_image_filename = Column(String, nullable=False)


class ProductImage(Base):
    __tablename__ = 'product_image'

    product_image_id = Column(Integer, primary_key=True)
    product_id = Column(
        Integer, ForeignKey('product.product_id'), nullable=False)
    product_image_description = Column(String, nullable=False)
    product_image_file = Column(String, nullable=False)


class DynamicBasketModel(Base):
    __tablename__ = 'dynamic_basket'

    dynamic_basket_id = Column(Integer, primary_key=True)
    user_id = Column(
        GUID, ForeignKey('user_account.user_id'))
    product_id = Column(
        Integer, ForeignKey('product.product_id'))
    dynamic_basket_quantity = Column(Integer, nullable=False)
    dynamic_basket_date = Column(DateTime(timezone=True), nullable=False)

    __table_args__ = (UniqueConstraint('user_id', 'product_id', name='dynamic_basket_product'),)

class StandardBasketModel(Base):
    __tablename__ = 'standard_basket'

    standard_basket_id = Column(Integer, primary_key=True)
    user_id = Column(
        GUID, ForeignKey('user_account.user_id'))
    stock_item_id = Column(
        Integer, ForeignKey('stock_item.stock_item_id'))
    standard_basket_quantity = Column(Integer, nullable=False)
    standard_basket_date = Column(DateTime(timezone=True), nullable=False)

    __table_args__ = (UniqueConstraint('user_id', 'stock_item_id', name='standard_basket_stock'),)


class ServiceCancellationModel(Base):
    __tablename__ = 'delivery_cancelation'

    delivery_cancelation_id = Column(Integer, primary_key=True)
    delivery_service_id = Column(
        Integer, ForeignKey('delivery_service.delivery_service_id'))
    credit_id = Column(Integer)
    delivery_cancelation_reason = Column(Integer)
    delivery_cancelation_date = Column(DateTime(timezone=True))


class DeliveryPersonModel(Base):
    __tablename__ = 'delivery_person'

    delivery_person_id = Column(Integer, primary_key=True)
    user_id = Column(GUID, ForeignKey('user_account.user_id'), nullable=False)
    delivery_person_identification_type_id = Column(Integer, nullable=False)
    delivery_person_identification = Column(String, nullable=False)
    delivery_person_birth_date = Column(Date, nullable=False)
    delivery_person_address = Column(String, nullable=False)
    delivery_person_phone = Column(String, nullable=True)
    delivery_person_date = Column(DateTime(timezone=True), nullable=False)


class DeliveryPersonStatusModel(Base):
    __tablename__ = 'delivery_person_status'

    delivery_person_status_id = Column(Integer, primary_key=True)
    delivery_person_id = Column(Integer, ForeignKey('delivery_person.delivery_person_id'), nullable=False)
    delivery_person_is_online = Column(Boolean, nullable=True)
    delivery_person_status_date = Column(DateTime(timezone=True), nullable=False)

class DeliveryPersonLocationModel(Base):
    __tablename__ = 'delivery_person_location'

    delivery_person_location_id = Column(Integer, primary_key=True)
    delivery_person_id = Column(Integer, ForeignKey('delivery_person.delivery_person_id'), nullable=False)
    delivery_service_id = Column(Integer, nullable=False)
    delivery_person_location = Column(Integer, nullable=False)
    delivery_person_location_date = Column(String, nullable=False)


class DeliveryServiceModel(Base):
    __tablename__ = 'delivery_service'

    delivery_service_id = Column(Integer, primary_key=True)
    delivery_person_id = Column(Integer, ForeignKey('delivery_person.delivery_person_id'),  nullable=False)
    user_address_id = Column(Integer, ForeignKey('user_address.user_address_id'),  nullable=False)
    product_order_id = Column(Integer, ForeignKey('product_order.product_order_id'),  nullable=False)


class DeliveryServiceStatusModel(Base):
    __tablename__ = 'delivery_service_status'

    delivery_service_status_id = Column(Integer, primary_key=True)
    delivery_service_id = Column(Integer, ForeignKey('delivery_person.delivery_person_id'),  nullable=False)
    delivery_service_status = Column(Integer, ForeignKey('user_address.user_address_id'),  nullable=False)
    delivery_service_status_date = Column(Integer, ForeignKey('product_order.product_order_id'),  nullable=False)



class DeliveryVehicle(Base):
    __tablename__ = 'delivery_vehicle'

    delivery_vehicle_id = Column(Integer, primary_key=True)
    delivery_person_id = Column(Integer, ForeignKey('delivery_person.delivery_person_id'), nullable=False)
    delivery_person_type = Column(Integer, nullable=False)
    delivery_person_plate = Column(String, nullable=True)
    delivery_person_description = Column(String, nullable=False)


class StoreModel(Base):
    __tablename__ = 'store'

    store_id = Column(GUID, primary_key=True)
    _store_category_id = Column(Integer, ForeignKey('store_category.store_category_id'), nullable=False)
    _store_name = Column(String, nullable=False, unique=True, index=True)
    _store_phone = Column(String, nullable=False)
    store_date = Column(DateTime(timezone=True), nullable=False)



class StoreLocationModel(Base):
    __tablename__ = 'store_location'

    _store_id = Column(GUID, ForeignKey('store.store_id'), nullable=False, primary_key=True)
    _city_id = Column(Integer, ForeignKey('city.city_id'), nullable=False)
    store_gps = Column(Geometry(geometry_type='POINT'), nullable=False)
    _store_address = Column(String, nullable=False)


class StoreCategoryModel(Base):
    __tablename__ = 'store_category'

    store_category_id = Column(Integer, primary_key=True)
    store_category = Column(String, nullable=False)

class StoreEmployeeModel(Base):
    __tablename__ = 'store_employee'

    store_employee_id = Column(Integer, primary_key=True)
    _user_id = Column(GUID, ForeignKey('user_account.user_id'), index=True, nullable=False)
    _store_id = Column(GUID, ForeignKey('store.store_id'), index=True, nullable=False)

    __table_args__ = (UniqueConstraint('_user_id', '_store_id', name='unique_employee'),)


class EmployeeRequestStatusModel(Base):
    __tablename__ = 'employee_request_status'

    store_employee_status_id = Column(Integer, primary_key=True)
    _store_employee_id = Column(Integer, ForeignKey('store_employee.store_employee_id'), nullable=False)
    _request_status = Column(Integer, nullable=False)
    _requested_by = Column(GUID, ForeignKey('user_account.user_id'), nullable=False)
    request_date = Column(DateTime(timezone=True), nullable=False, default=datetime.datetime.now)

class StoreEmployeeRoleModel(Base):
    __tablename__ = 'store_employee_role'

    store_employee_role_id = Column(Integer, primary_key=True)
    _store_employee_id = Column(Integer, ForeignKey('store_employee.store_employee_id'), nullable=False)
    _store_employee_role = Column(Integer, nullable=False)
    _requested_by = Column(GUID, ForeignKey('user_account.user_id'), nullable=False)
    request_date = Column(DateTime(timezone=True), nullable=False, default=datetime.datetime.now)

class StoreHoursModel(Base):
    __tablename__ = 'store_hours'

    store_hours_id = Column(Integer, primary_key=True)
    _store_id = Column(GUID, ForeignKey('store.store_id'), nullable=False)
    _day = Column(Integer, nullable=False)
    store_open = Column(Time, default=datetime.time(8, 0), nullable=False)
    store_close = Column(Time, default=datetime.time(22, 0), nullable=False)

    __table_args__ = (UniqueConstraint('_store_id', '_day', name='unique_store_hours'),)