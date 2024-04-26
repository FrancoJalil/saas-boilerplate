from paypal.helpers.credentials import PaypalToken, clientID, clientSecret
import requests
from helpers.email import send_email
from .models import Purchase, PaypalProductModel


# paypal custom order
def get_product_from_cart(cart):
    product_id = cart[0]["id"]
    product = PaypalProductModel.objects.get(paypal_id_product=product_id)
    return product


def create_paypal_order(user, product, value):
    access_token = PaypalToken()
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}',
    }

    data = {
        "purchase_units": [
            {
                "amount": {
                    "currency_code": "USD",
                    "value": value,
                },
                "custom_id": product.paypal_id_product,
                "reference_id": "CUSTOM"
            }
        ],
        "intent": "CAPTURE",
        "payment_source": {
            "paypal": {
                "experience_context": {
                    "payment_method_preference": "IMMEDIATE_PAYMENT_REQUIRED",
                    "payment_method_selected": "PAYPAL",
                    "brand_name": "EXAMPLE INC",
                    "shipping_preference": "NO_SHIPPING",
                    "locale": "en-US",
                    "landing_page": "NO_PREFERENCE",
                    "payment_method_preference": "IMMEDIATE_PAYMENT_REQUIRED",
                    "user_action": "PAY_NOW",
                    "cancel_url": product.home_url
                }
            }
        }
    }

    response = requests.post(
        "https://api.sandbox.paypal.com/v2/checkout/orders",
        headers=headers,
        json=data
    )
    response.raise_for_status()

    return response.json()


# capture order
def capture_paypal_payment(order_id):

    token = PaypalToken()
    capture_url = f"https://api.sandbox.paypal.com/v2/checkout/orders/{order_id}/capture"
    headers = {"Content-Type": "application/json",
               "Authorization": "Bearer " + token}

    response = requests.post(capture_url, headers=headers)
    response.raise_for_status()
    return response.json()


def process_completed_payment(user, capture_response):
    purchase_units = capture_response.get('purchase_units')
    reference_id = purchase_units[0].get('reference_id')

    if reference_id == 'CUSTOM':
        num_tokens = calculate_tokens(capture_response)
        user = add_tokens_to_user(user, num_tokens)
        send_email("buy_custom", user.email, context={
            "tokens": int(float(num_tokens))})


def calculate_tokens(capture_response):
    purchase_units = capture_response.get('purchase_units')
    amount_value = purchase_units[0]['payments']['captures'][0]['amount']['value']
    return int(float(amount_value))  # Assuming 1 token = $1


def add_tokens_to_user(user, num_tokens):
    user.tokens += num_tokens
    user.save()
    return user


def create_purchase_record(user, capture_response):
    purchase_units = capture_response.get('purchase_units')
    custom_id = purchase_units[0]['payments']['captures'][0]['custom_id']
    amount_value = purchase_units[0]['payments']['captures'][0]['amount']['value']

    product = PaypalProductModel.objects.get(paypal_id_product=custom_id)
    purchase = Purchase(user=user, product=product, price=amount_value)
    purchase.save()
