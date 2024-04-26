from twilio.base.exceptions import TwilioException

from twilio.rest import Client

from dotenv import load_dotenv
import os

load_dotenv()


account_sid = os.environ.get('ACCOUNT_SID')
auth_token = os.environ.get('AUTH_TOKEN')
verify_sid = os.environ.get('VERIFY_SID')


def send_sms(num):
    client = Client(account_sid, auth_token)
    try:
        verification = client.verify.v2.services(verify_sid) \
            .verifications \
            .create(to=num, channel="sms")


        return verification.status
    except Exception as e:
        print(str(e))
        return False


def verify_otp_sms(otp_code, num):

    try:
        client = Client(account_sid, auth_token)
        verification_check = client.verify.v2.services(verify_sid) \
            .verification_checks \
            .create(to=num, code=otp_code)

        return verification_check.status

    except TwilioException as e:
        print(f"TwilioException: {e}")
        # Handle the exception as needed
        return "error"
