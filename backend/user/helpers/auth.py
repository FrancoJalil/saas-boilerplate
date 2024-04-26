from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
import requests
from user.serializers import MyTokenObtainPairSerializer
from dotenv import load_dotenv
import os
load_dotenv()

client_id = os.environ.get('GOOGLE_CLIENT_ID')

def get_google_id_info(validated_data):
    token = validated_data['userInfo'].get('credential')
    
    if token:
        return id_token.verify_oauth2_token(token, google_requests.Request(), client_id), token
    else:
        access_token = validated_data['userInfo'].get('access_token')
        userinfo_url = f'https://www.googleapis.com/oauth2/v3/userinfo?access_token={access_token}'
        response = requests.get(userinfo_url)
        return response.json(), access_token


def check_google_credentials(tok):
    try:
        id_token.verify_oauth2_token(tok, google_requests.Request(), client_id)
        return True
    except:
        pass
    
    
    userinfo_url = f'https://www.googleapis.com/oauth2/v3/userinfo?access_token={tok}'
    response = requests.get(userinfo_url)
    if response.status_code == 200:
        return True
    else:
        return False


def get_user_or_create_otps(email):
    from user.models import CustomUser, OtpCode
    try:
        user = CustomUser.objects.get(email=email)
        return user, False
    except CustomUser.DoesNotExist:
        user_otp_code, _ = OtpCode.objects.get_or_create(email=email)
        user_otp_code.save()
        return user_otp_code, True

def get_user_tokens(user):
    tokens = MyTokenObtainPairSerializer().get_token(user)

    return {
        'refresh': str(tokens),
        'access': str(tokens.access_token),
    }


