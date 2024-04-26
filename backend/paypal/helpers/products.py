from paypal.helpers.credentials import PaypalToken, clientID, clientSecret
import requests

def create_product(name, description, home_url):

    from paypal.models import PaypalProductModel

    access_token = PaypalToken()

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'PayPal-Request-Id': f'PRODUCT-{name}',
        'Prefer': 'return=representation',
        'Authorization': 'Bearer ' + access_token
    }

    data = '{"name": "' + name + '", "description": "' + description + \
        '", "type": "SERVICE", "category": "SOFTWARE", "image_url": "https://example.com/streaming.jpg", "home_url": "' + home_url + '"}'

    response = requests.post(
        'https://api-m.sandbox.paypal.com/v1/catalogs/products', headers=headers, data=data)

    response_json = response.json()
    product_id = response_json['id']

    paypal_product = PaypalProductModel.objects.get(name=name)
    paypal_product.paypal_id_product = product_id
    paypal_product.save()

