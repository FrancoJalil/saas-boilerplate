import os
import base64
import requests

from dotenv import load_dotenv
load_dotenv()

clientID = os.environ.get('PAYPAL_CLIENT_ID')
clientSecret = os.environ.get('PAYPAL_CLIENT_SECRET')


def PaypalToken():

    url = "https://api.sandbox.paypal.com/v1/oauth2/token"
    data = {
        "client_id": clientID,
        "client_secret": clientSecret,
        "grant_type": "client_credentials"
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": "Basic {0}".format(base64.b64encode((clientID + ":" + clientSecret).encode()).decode())
    }

    token = requests.post(url, data, headers=headers)

    return token.json()['access_token']
