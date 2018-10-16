import mercadopago
from dbmodel.res.custom_exceptions import ResourceConflict
import json
from requests.exceptions import ConnectionError


access_token = "TEST-7417458935207415-111422-a410711bcff8b4e8f1c4c04fbac5cf4a__LC_LB__-62001234"
public_key = "TEST-0aa2ffe9-466a-43c9-b052-06c7aca85367"
mp = mercadopago.MP(access_token)

def new_customer(data):
    result = mp.post("/v1/customers", data)
    print("Usuario creado:", result)
    return result

def payment(data):
    data['installments'] = 1
    result = mp.post("/v1/payments", data)

    print("Respuesta estado transaccion:", result['response']['status'])
    if result['response']['status'] != 'approved':
        return True, result
    return False, result

def get_customer_id(email):
    filters = {
        "email": email
    }
    try:
        customer = mp.get("/v1/customers/search", filters)
        if customer['response']['paging']['total'] == 0:
            raise ResourceConflict('Este usuario no se encuentra resgistrado en la base de datos de Mercado Libre')
    except ConnectionError:
        print("Conexion rechazada")

    return customer["response"]["results"][0]["id"]

def get_stored_cards(email):
    error, customer_id = get_customer_id(email)
    if error:
        return True, customer_id

    cards = mp.get("/v1/customers/" + customer_id + "/cards")

    print(cards["response"])
    return False, cards


def store_card(email, token):
    error, customer_id = get_customer_id(email)
    if error:
        return True, customer_id

    card = mp.post("/v1/customers/" + customer_id + "/cards", {"token": token})
    print("Estado creacion tarjeta:", card['status'],"id tarjeta:", card['response']['id'] )

    if card['status'] != 200:
        resp = [400, {'message': 'Esta tarjeta ya existe',
                      'action': ''}]
        return True, resp
    resp = [201, {'message': 'La tarjeta se ha guardado exitosamente'}]
    return False, resp