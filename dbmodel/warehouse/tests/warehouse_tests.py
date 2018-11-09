import unittest
import pytz
from dbmodel.database_init import create_database, drop_database
from dbmodel.res.custom_exceptions import InvalidArgument, ResourceConflict
from dbmodel.user.user_data import User, get_user_by_mail
from dbmodel.warehouse.warehouse_data import Warehouse, WarehouseLocation, \
    get_warehouse_by_location, get_warehouse_by_id, check_warehouse_not_exists_by_name, \
    WarehouseMember, get_user_warehouse_memberships, get_warehouse_members, WarehouseMemberStatus, \
    update_warehouse_member_status, update_warehouse_member_role, WarehouseMemberRole, WarehouseOpeningHours, \
    check_schedule_exists_by_warehouse


class WarehouseTest(unittest.TestCase):

    def setUp(self):
        drop_database()
        create_database()
        User('Daniel Machado Castillo', 'danielmcis@hotmail.com', '+573138966044', 'Freqm0d+', 1).add_item()
        User('Yoshi Restall', 'yrestall0@army.mil', '926-587-9732', 'Freqm0d+', 1).add_item()

    def tearDown(self):
        # drop_database()
        pass

    def test_construct_warehouse_object_with_bad_argument(self):
        with self.assertRaises(InvalidArgument):
            Warehouse("", 'La Tienda', "Calle 73 # 7-51 Apto 401", -74.055353, 4.656351, 1, "3046628054")
        with self.assertRaises(InvalidArgument):
            Warehouse(1, '', "Calle 73 # 7-51 Apto 401", -74.055353, 4.656351, 1, "3046628054")
        with self.assertRaises(InvalidArgument):
            Warehouse(1, 'La Tienda', "", -74.055353, 4.656351, 1, "3046628054")
        with self.assertRaises(InvalidArgument):
            Warehouse(1, 'La Tienda', "Calle 73 # 7-51 Apto 401", -74.055353, "", 1, "3046628054")
        with self.assertRaises(InvalidArgument):
            Warehouse(1, 'La Tienda', "Calle 73 # 7-51 Apto 401", "", 4.656351, 1, "3046628054")
        with self.assertRaises(InvalidArgument):
            Warehouse(1, 'La Tienda', "Calle 73 # 7-51 Apto 401", -74.055353, 4.656351, "", "3046628054")
        with self.assertRaises(InvalidArgument):
            Warehouse(1, 'La Tienda', "Calle 73 # 7-51 Apto 401", -74.055353, 4.656351, 1, "")

    def test_get_warehouse_object(self):
        test_warehouse = Warehouse(1, 'La Tienda', "Calle 73 # 7-51 Apto 401", -74.055353, 4.656351, 1,
                                   "3046628054")
        test_warehouse.add_item()
        warehouse = get_warehouse_by_location([-74.054437, 4.659212])
        self.assertIsInstance(warehouse[0], Warehouse)
        self.assertIsInstance(warehouse[0].ubicacion, WarehouseLocation)
        warehouse = get_warehouse_by_id(test_warehouse.id_almacen)
        self.assertIsInstance(warehouse, Warehouse)
        self.assertIsInstance(warehouse.ubicacion, WarehouseLocation)
        with self.assertRaises(ResourceConflict):
            check_warehouse_not_exists_by_name(test_warehouse.nombre)

    def test_add_warehouse_member(self):
        test_user = get_user_by_mail('danielmcis@hotmail.com')
        test_user_1 = get_user_by_mail('yrestall0@army.mil')
        test_warehouse = Warehouse(1, 'La Tienda', "Calle 73 # 7-51 Apto 401", -74.055353, 4.656351, 1,
                                   "3046628054")
        test_warehouse.add_item()
        with self.assertRaises(InvalidArgument):
            WarehouseMember("", test_warehouse.id_almacen, test_user.id_usuario)
        with self.assertRaises(InvalidArgument):
            WarehouseMember(test_user_1.id_usuario, "",test_user.id_usuario)
        test_member = WarehouseMember(test_user_1.id_usuario, test_warehouse.id_almacen, test_user.id_usuario)
        test_member.add_warehouse_member()
        update_warehouse_member_status(test_member.id_miembro_almacen, 2, test_user.id_usuario)
        update_warehouse_member_role(test_member.id_miembro_almacen, 1, test_user.id_usuario)


    def test_add_warehouse_schedule(self):
        test_warehouse = Warehouse(1, 'La Tienda', "Calle 73 # 7-51 Apto 401", -74.055353, 4.656351, 1,
                                   "3046628054")
        test_warehouse.add_item()
        test_warehouse_schedule = WarehouseOpeningHours(test_warehouse.id_almacen, 1, 8, 0, 22, 0)
        test_warehouse_schedule.add_warehouse_schedule()
        check_schedule_exists_by_warehouse(test_warehouse.id_almacen, 8)
        WarehouseOpeningHours(test_warehouse.id_almacen, 2, 8, 0, 22, 0).add_warehouse_schedule()
        WarehouseOpeningHours(test_warehouse.id_almacen, 3, 8, 0, 22, 0).add_warehouse_schedule()
        WarehouseOpeningHours(test_warehouse.id_almacen, 4, 8, 0, 22, 0).add_warehouse_schedule()
        WarehouseOpeningHours(test_warehouse.id_almacen, 5, 8, 0, 22, 0).add_warehouse_schedule()
        WarehouseOpeningHours(test_warehouse.id_almacen, 6, 8, 0, 22, 0).add_warehouse_schedule()
        WarehouseOpeningHours(test_warehouse.id_almacen, 7, 8, 0, 20, 0).add_warehouse_schedule()
        WarehouseOpeningHours(test_warehouse.id_almacen, 8, 8, 0, 20, 0).add_warehouse_schedule()




if __name__ == '__main__':
    unittest.main()
