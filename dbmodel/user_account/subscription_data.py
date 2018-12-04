import calendar
import datetime

from sqlalchemy import and_

from dbmodel.dbconfig import s
# from dbmodel.database_model import SubscriptionGroupModel, SubscriptionMemberModel,SubscriptionMemberHistoryModel, SubscriptionPlanModel
#
#
# class SubscriptionGroup(SubscriptionGroupModel):
#
#     def get_subscription_status(self):
#         subscription_status = {1: 'Activa',
#                                2: 'Pendiente',
#                                3: 'Finalizada',}
#         return subscription_status.get(self.id_estado_suscripcion)
#
#     @property
#     def serialize(self):
#         """Return object data in easily serializeable format"""
#         miembro = self.miembro
#         orden = self.orden
#         return {
#             'id_suscripcion': self.id_grupo_suscripcion,
#             'plan': self.plan_suscripcion.serialize,
#             'estado': self.get_subscription_status(),
#             'fecha_inicio': self.fecha_inicio.strftime("%Y-%m-%d %H:%M:%S %Z"),
#             'fecha_final': self.get_end_date(self.fecha_inicio, self.plan_suscripcion.duracion_plan).strftime("%Y-%m-%d %H:%M:%S %Z"),
#             'fecha_renovarl': self.get_renew_date(self.fecha_inicio, self.plan_suscripcion.duracion_plan).strftime("%Y-%m-%d %H:%M:%S %Z"),
#             'renovar': self.renovar,
#             'miembros': self.make_list(miembro),
#             'orden': self.make_list(orden)
#         }
#
#     @staticmethod
#     def make_list(item_list):
#         final_list = []
#         for item in item_list:
#             final_list.append(item.serialize)
#         return final_list
#
#     def compare_number_members(self, plan):
#         error, resp = SubscriptionPlan.get_number_members(plan)
#         return resp-len(self.miembro)
#
#     def change_subscription_status(self, status):
#         self.id_estado_suscripcion = status
#         s.commit()
#         error, resp = False, [201, {'message': 'Se ha cambiado el estado de la suscripcion exitosamente'}]
#         return error, resp
#
#     @staticmethod
#     def get_item(item_id):
#         item = s.query(SubscriptionGroup).filter(
#             SubscriptionGroup.id_grupo_suscripcion == item_id).first()
#         if not item:
#             error = [404, {'message': 'Este grupo no existe',
#                            'action': 'Realice una nueva consulta'}]
#             return True, error
#         return False, item
#
#     def get_end_date(self, start_date, plan_duration):
#
#         return self.get_renew_date(start_date, plan_duration) - datetime.timedelta(days=1)
#
#     @staticmethod
#     def get_renew_date(start_date, plan_duration):
#         month = start_date.month - 1 + plan_duration
#         year = int(start_date.year + month / 12)
#         month = month % 12 + 1
#         day = min(start_date.day, calendar.monthrange(year, month)[1])
#         return start_date.replace(year, month, day)
#
#     def renew_subscription(self):
#         if self.id_plan_suscripcion == 1:
#             resp = [409, {'message': 'El plan gratuito no se puede renovar',
#                           'action': 'Cambie a un plan pago para usar esta funcion'}]
#             return True, resp
#         self.fecha_inicio = datetime.datetime.now()
#         s.commit()
#         error, resp = False, [201, {'message': 'La suscripción se ha renovado exitosamente'}]
#         return error, resp
#
#     def add_item(self, user_account):
#         self.id_plan_suscripcion = 1
#         self.id_estado_suscripcion = 1
#         self.renovar = True
#         self.fecha_inicio = datetime.datetime.now()
#         s.add(self)
#         s.commit()
#         # s.close()
#         error, resp = SubscriptionMember().add_item(self, user_account, user_account)
#         if error:
#             return True, resp
#         resp = [201, {'message': 'La suscripción se ha creado exitosamente'}]
#         return False, resp
#
#     def change_item(self, plan):
#         if datetime.datetime.now() < self.get_end_date(self.fecha_inicio, self.plan_suscripcion.duracion_plan).replace(tzinfo=None):
#             resp = [409, {'message': 'Aun existe una suscripcion activa',
#                           'action': 'Espere hasta el final de la suscripcion e intente cambiar o renovar el plan'}]
#             return True, resp
#         if plan.id_plan < self.id_plan_suscripcion:
#             resp = [409, {'message': 'La suscripcion no se cambio, su plan actual es mas alto que el seleccionado',
#                           'action': 'Seleccione un plan mayor al actual'}]
#             return True, resp
#         if plan.id_plan == self.id_plan_suscripcion:
#             resp = [409, {'message': 'La suscripcion no se cambio, ya se encuentra en este plan',
#                           'action': 'Seleccione un plan diferente al actual'}]
#             return True, resp
#         self.id_plan_suscripcion = plan.id_plan
#         self.id_estado_suscripcion = 2
#         self.fecha_inicio = datetime.datetime.now()
#         self.renovar = True
#         s.commit()
#         resp = [201, {'message': 'La suscripción se ha cambiado exitosamente'}]
#         return False, resp
#
#     def change_suscription_plan(self, plan):
#         self.plan_suscripcion = plan
#         s.commit()
#
#     def toggle_suscription_renew(self):
#         if self.renovar is True:
#             self.renovar = False
#         else:
#             self.renovar = True
#         s.commit()
#
#
# class SubscriptionMember(SubscriptionMemberModel):
#
#     @property
#     def serialize(self):
#         """Return object data in easily serializeable format"""
#         return {
#             'id_miembro': self.id_miembro_suscripcion,
#             'usuario': self.usuario.nombre_completo,
#             'titular': self.titular,
#             'estado': self.historia[0].get_subscription_member_status()
#         }
#
#     @staticmethod
#     def get_item_titular(user_account):
#         item = s.query(SubscriptionMember).filter(
#             and_(SubscriptionMember.id_usuario == user_account, SubscriptionMember.titular == True)).first()
#         if not item:
#             error = [404, {'message': 'Este miembro no existe',
#                            'action': 'Realice una nueva consulta'}]
#             return True, error
#         return False, item
#
#     def add_item(self, group, user_account, updated_by):
#         if len(group.miembro) >= group.plan_suscripcion.cantidad_beneficiarios:
#             error = [404, {'message': 'Se ha alcanzado el limite de beneficiarios para este plan',
#                            'action': 'Elimine beneficiarios o actualice su plan'}]
#             return True, error
#         self.id_usuario = user_account
#         self.id_grupo_suscripcion = group.id_grupo_suscripcion
#         if user_account == updated_by:
#             self.titular = True
#         # updated_by = self.id_miembro_suscripcion
#         s.add(self)
#         s.commit()
#         # s.close()
#         error, resp = SubscriptionMemberHistory().add_item(self.id_miembro_suscripcion, 1, updated_by)
#         if error:
#             return True, resp
#         resp = [201, {'message': 'El miembro de la suscripción se ha creado exitosamente'}]
#         return False, resp
#
#     def delete_item(self):
#         error, resp = SubscriptionMemberHistory().add_item(self.id_miembro_suscripcion, 4, self.id_miembro_suscripcion)
#         if error:
#             return True, resp
#         resp = [201, {'message': 'El miembro de la suscripción se ha eliminado exitosamente'}]
#         return False, resp
#
#
# class SubscriptionMemberHistory(SubscriptionMemberHistoryModel):
#
#     def get_subscription_member_status(self):
#         subscription_member_status = {1: 'Pendiente',
#                                       2: 'Activo',
#                                       3: 'Declinado',
#                                       4: 'Retirado'}
#         return subscription_member_status.get(self.id_estado_miembro_suscripcion)
#
#     def add_item(self, member, state, updated_by):
#         self.id_miembro_suscripcion = member
#         self.id_estado_miembro_suscripcion = state
#         self.id_actualizado_por = updated_by
#         self.fecha_actualizacion = datetime.datetime.now()
#         s.add(self)
#         s.commit()
#         # s.close()
#         resp = [201, {'message': 'La historia de miembro de suscripción se ha creado exitosamente'}]
#         return False, resp
#
#
# class SubscriptionPlan(SubscriptionPlanModel):
#
#     @property
#     def serialize(self):
#         """Return object data in easily serializeable format"""
#         return {
#             'id_plan': self.id_plan,
#             'nombre': self.nombre_plan,
#             'cantidad_miembros': self.cantidad_beneficiarios,
#             'limite_servicios': self.limite_servicios,
#             'precio_plan': self.precio_plan,
#             'duracion_plan': self.duracion_plan
#         }
#
#     @staticmethod
#     def get_plan_info(item_id):
#         item = s.query(SubscriptionPlan).filter(
#             SubscriptionPlan.id_plan == item_id).first()
#         if not item:
#             error = [404, {'message': 'Este plan no existe',
#                            'action': 'Realice una nueva consulta'}]
#             return True, error
#         return False, item
