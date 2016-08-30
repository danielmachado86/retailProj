import json
import urllib
import urllib.parse
import urllib.request
import urllib.error


def transaction(data):
    url = "https://test.oppwa.com/v1/payments"
    # data = {
    #     'authentication.userId': userid,
    #     'authentication.password': password,
    #     'authentication.entityId': entityid,
    #     'amount': amount,
    #     'currency': currency,
    #     'paymentBrand': payment_brand,
    #     'paymentType': payment_type,
    #     'card.number': c_number,
    #     'card.holder': c_holder,
    #     'card.expiryMonth': c_expiry_month,
    #     'card.expiryYear': c_expiry_year,
    #     'card.cvv': c_cvv,
    #     'merchantTransactionId': transactionid,
    #     'testMode': 'EXTERNAL'
    # }
    data = urllib.parse.urlencode(data)
    binary_data = data.encode('utf-8')
    request = urllib.request.Request(url)
    try:
        response = urllib.request.urlopen(request, data=binary_data)
        resp = response.read()
        resp = json.loads(resp.decode('utf-8'))
        result = resp.get('result')
        code = result.get('code')
        description = result.get('description')
        id_transaction = resp.get('id')
        if code == '000.100.112':
            error = False
        else:
            error = True
        resp = [code, description, id_transaction]
        return error, resp
    except urllib.error.HTTPError as e:
        resp = e.read()
        resp = json.loads(resp.decode('utf-8'))
        result = resp.get('result')
        code = result.get('code')
        description = result.get('description')
        id_transaction = resp.get('id')
        resp = [code, description, id_transaction]
        return True, resp
