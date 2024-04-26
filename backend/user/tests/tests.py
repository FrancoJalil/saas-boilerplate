from .setup import SetUpAuthUser
from django.shortcuts import get_object_or_404
from rest_framework.test import APITestCase
from faker import Faker
from django.urls import reverse
from rest_framework import status
from ..models import CustomUser, OtpCode
fake = Faker()


class TestRefreshToken(SetUpAuthUser):

    def test_refresh_access_token(self):
        self.token_refresh_url = reverse("auth_refresh")

        response = self.client.post(
            self.token_refresh_url,
            {'refresh': self.refresh_token},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        new_access_token = response.data.get("access")

        self.user_data = reverse("user_data")
        headers = {'Authorization': f'Bearer {new_access_token}'}
        response = self.client.get(self.user_data, headers=headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invalid_refresh_access_token(self):
        self.token_refresh_url = reverse("auth_refresh")
        response = self.client.post(
            self.token_refresh_url,
            {'refresh': "123"},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_empty_refresh_access_token(self):
        self.token_refresh_url = reverse("auth_refresh")
        response = self.client.post(
            self.token_refresh_url,
            {'refresh': ""},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class TestSendCodeForgotPassword(APITestCase):

    def setUp(self):

        self.forgot_url = reverse("otp_change_password")
        self.email = fake.email()
        self.invalid_email = 'f21r21'
        self.unregistered_mail = fake.email()
        self.user = CustomUser.objects.create_superuser(
            first_name="Developer",
            last_name="Developer",
            email=self.email
        )

    def test_code_sended(self):
        response = self.client.get(
            self.forgot_url,
            {'email': self.email},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_code_sended_to_unregistered_mail(self):
        response = self.client.get(
            self.forgot_url,
            {'email': self.unregistered_mail},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertEqual(response.data.get("msg"), "Invalid field 'Email': Email not registered.")
        

    def test_code_sended_to_invalid_email(self):
        response = self.client.get(
            self.forgot_url,
            {'email': self.invalid_email},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertEqual(response.data.get("msg"), "Invalid field 'Email': Enter a valid email address.")
        


class TestCheckCodeForgotPassword(APITestCase):
    def setUp(self):
        self.otp_change_password = reverse("otp_change_password")
        self.email = fake.email()
        self.invalid_email = 'f21r21'
        self.unregistered_mail = fake.email()
        self.user = CustomUser.objects.create_superuser(
            first_name="Developer",
            last_name="Developer",
            email=self.email
        )

        # SEND CODE TO RIGHT MAIL
        response = self.client.get(
            self.otp_change_password,
            {'email': self.email},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        otp_code_forgot = OtpCode.objects.filter(
            email=self.email).first()
        self.otp_right = otp_code_forgot.otp
        self.otp_wrong = "x23123"

    def test_check_code_sended(self):
        response = self.client.post(
            self.otp_change_password,
            {'email': self.email,
             'otp': self.otp_right},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_check_code_to_unregistered_mail(self):
        response = self.client.post(
            self.otp_change_password,
            {'email': self.unregistered_mail,
             'otp': self.otp_wrong},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertEqual(response.data.get("msg"), "Invalid field 'Email': Email not registered.")

        

    def test_code_sended_to_invalid_email(self):
        response = self.client.post(
            self.otp_change_password,
            {'email': self.invalid_email,
             'otp': self.otp_wrong},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertEqual(response.data.get("msg"), "Invalid field 'Email': Enter a valid email address.")
        


class TestChangePasswordForgotPassword(APITestCase):
    def setUp(self):
        self.otp_change_password = reverse("otp_change_password")

        self.change_password = reverse("change_password")
        self.email = fake.email()
        self.invalid_email = 'f21r21'
        self.unregistered_mail = fake.email()
        self.user = CustomUser.objects.create_superuser(
            first_name="Developer",
            last_name="Developer",
            email=self.email
        )

        # SEND CODE TO RIGHT MAIL
        response = self.client.get(
            self.otp_change_password,
            {'email': self.email},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        otp_code_forgot = OtpCode.objects.filter(
            email=self.email).first()
        self.otp_right = otp_code_forgot.otp
        self.otp_wrong = "x23123"

    def test_change_password_with_valid_email(self):
        response = self.client.post(
            self.change_password,
            {'email': self.email,
             'otp': self.otp_right,
             'new_password': fake.password()},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_change_password_with_unregistered_mail(self):
        response = self.client.post(
            self.change_password,
            {'email': self.unregistered_mail,
             'otp': self.otp_wrong,
             'new_password': fake.password()},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertEqual(response.data.get("msg"), "Invalid field 'Email': Email not registered.")



    def test_change_password_with_invalid_email(self):
        response = self.client.post(
            self.change_password,
            {'email': self.invalid_email,
             'otp': self.otp_wrong,
             'new_password': fake.password()},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get("msg"), "Invalid field 'Email': Enter a valid email address.")
        

    def test_change_password_with_other_otp_action_type(self):

        otp_google, _ = OtpCode.objects.get_or_create(
            email=self.email)
        otp_google.action_type = "google"
        otp_google.save()

        response = self.client.post(
            self.change_password,
            {'email': self.email,
             'otp': otp_google.otp,
             'new_password': fake.password()},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get("msg"),
                         "Code not generated yet.")


class TestCheckEmail(APITestCase):

    def setUp(self):

        self.check_url = reverse("continue_with_email")
        self.email_exists = fake.email()
        self.email_does_not_exist = fake.email()
        self.invalid_email = 'invalidemail'
        self.user = CustomUser.objects.create_superuser(
            first_name="Developer",
            last_name="Developer",
            email=self.email_exists
        )

    def test_continue_with_email_exists(self):
        response = self.client.post(
            self.check_url,
            {'email': self.email_exists},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data.get("email_exists"))

    def test_continue_with_email_does_not_exist(self):
        response = self.client.post(
            self.check_url,
            {'email': self.email_does_not_exist},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data.get("email_exists"))

    def test_check_invalid_email(self):
        response = self.client.post(
            self.check_url,
            {'email': self.invalid_email},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIsNotNone(response.data.get('msg'))

        self.assertEqual(response.data.get("msg"), "Invalid field 'Email': Enter a valid email address.")
        


class TestCheckOtpEmail(APITestCase):

    def setUp(self):

        self.send_otp_url = reverse("continue_with_email")
        self.check_otp_signup = reverse("check_otp_signup")
        self.email_true = fake.email()
        self.email_false = fake.email()
        self.check_otp_signup_ungenerated_code = fake.email()
        self.invalid_email = "ffasfas"
        self.user = CustomUser.objects.create_superuser(
            first_name="Developer",
            last_name="Developer",
            email=self.email_true
        )

        response = self.client.post(
            self.send_otp_url,
            {'email': self.email_false},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_send_otp_email(self):
        user_otp_code = get_object_or_404(
            OtpCode, email=self.email_false)
        response = self.client.post(
            self.check_otp_signup,
            {'email': self.email_false,
             'otp': user_otp_code.otp},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_send_otp_email_registered(self):
        # user_otp_code = get_object_or_404(OtpCode, email=self.email_true)
        response = self.client.post(
            self.check_otp_signup,
            {'email': self.email_true,
             'otp': "213123"},
            format='json'
        )
        self.assertEqual(response.status_code, 400)

        self.assertIsNotNone(response.data.get('msg'))

        self.assertEqual(response.data.get("msg"), "Invalid field 'Email': Email is already registered.")
        

    def test_check_invalid_email(self):
        response = self.client.post(
            self.check_otp_signup,
            {'email': self.invalid_email,
             "otp": "123123"},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIsNotNone(response.data.get('msg'))

        self.assertEqual(response.data.get("msg"), "Invalid field 'Email': Enter a valid email address.")
        
        

    def test_send_otp_email_but_ungenerated_code(self):
        # user_otp_code = get_object_or_404(OtpCode, email=self.email_true)
        response = self.client.post(
            self.check_otp_signup,
            {'email': self.check_otp_signup_ungenerated_code,
             'otp': "213123"},
            format='json'
        )
        self.assertEqual(response.status_code, 404)


        self.assertEqual(response.data.get("msg"), "Code not generated yet.")
        
        


class TestRegisterUserFlow(APITestCase):

    def setUp(self):
        self.email_ok = fake.email()
        self.invalid_email = "co"
        self.password = "Cacara123"
        self.continue_with_email_url = reverse("continue_with_email")
        self.check_otp_signup_url = reverse("check_otp_signup")
        self.register_url = reverse("register")

    def continue_with_email(self, email):
        # EMAIL CHECK AND SEND OTP IF NEW
        response = self.client.post(
            self.continue_with_email_url,
            {'email': email},
            format='json'
        )
        return response

    def check_otp(self, email, otp):
        # CHECK IF OTP IS VALID
        response = self.client.post(
            self.check_otp_signup_url,
            {'email': email,
             'otp': otp},
            format='json'
        )
        return response

    def register_user(self, email, password, otp):
        # REGISTER USER
        response = self.client.post(
            self.register_url,
            {'email': email,
             'password': password,
             'otp': otp,
             'register_type': "email"},
            format='json'
        )
        return response

    def test_successful_registration_flow(self):

        response = self.continue_with_email(self.email_ok)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data.get("email_exists"))

        otp = OtpCode.objects.filter(email=self.email_ok).first().otp
        response = self.check_otp(self.email_ok, otp)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        response = self.register_user(self.email_ok, self.password, otp)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_successful_registration_simple_flow(self):

        response = self.continue_with_email(self.email_ok)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data.get("email_exists"))

        otp = OtpCode.objects.filter(email=self.email_ok).first().otp

        response = self.register_user(self.email_ok, self.password, otp)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_successful_registration_and_change_password_flow(self):
        # registration
        response = self.continue_with_email(self.email_ok)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data.get("email_exists"))

        otp = OtpCode.objects.filter(email=self.email_ok).first().otp
        response = self.check_otp(self.email_ok, otp)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        response = self.register_user(self.email_ok, self.password, otp)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # now change password
        self.otp_change_password = reverse("otp_change_password")
        response = self.client.get(
            self.otp_change_password,
            {'email': self.email_ok},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        otp_code_forgot = OtpCode.objects.filter(
            email=self.email_ok).first()

        self.otp_right = otp_code_forgot.otp

        self.change_password = reverse("change_password")
        response = self.client.post(
            self.change_password,
            {'email': self.email_ok,
             'otp': self.otp_right,
             'new_password': fake.password()},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class TestGetProtectedData(SetUpAuthUser):

    def test_get_data_from_user_data(self):
        self.user_data = reverse("user_data")

        headers = {'Authorization': f'Bearer {self.token}'}
        response = self.client.get(self.user_data, headers=headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], self.user.email)
        self.assertIsNotNone(response.data['tokens'])
        self.assertIsNotNone(response.data['verified'])
        self.assertIsNone(response.data['num'])

    def test_get_user_data_with_fields(self):

        self.user_data = reverse("user_data")

        headers = {'Authorization': f'Bearer {self.token}'}
        response = self.client.get(
            self.user_data + '?fields=email,num', headers=headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], self.user.email)
        self.assertIsNone(response.data['num'])
        self.assertNotIn('tokens', response.data.keys())
        self.assertNotIn('date_joined', response.data.keys())

    def test_get_user_data_invalid_field(self):

        self.user_data = reverse("user_data")

        headers = {'Authorization': f'Bearer {self.token}'}
        response = self.client.get(
            self.user_data + '?fields=password', headers=headers)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get(
            "msg"), "The field 'password' is not a valid field for the CustomUser model.")


class TestContactMe(SetUpAuthUser):
    def test_contact_me_success(self):
        self.contact_url = reverse("contact")

        headers = {'Authorization': f'Bearer {self.token}'}
        data = {'subject': 'Asunto xd', 'msg': 'msg xd'}
        response = self.client.post(
            self.contact_url, headers=headers, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_contact_me_empty(self):
        self.contact_url = reverse("contact")

        headers = {'Authorization': f'Bearer {self.token}'}
        data = {'subject': '', 'msg': 'example example example'}
        response = self.client.post(
            self.contact_url, headers=headers, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertEqual(response.data.get(
            "msg"), "Invalid field 'Subject': This field may not be blank.")


""" WARNING: THIS TESTS SPEND TWILIO TOKENS
class TestSendOtpSMS(SetUpAuthUser):

    def setUp(self):
        super().setUp()
        self.user.verified = False
        self.user.save()
        self.otp_sms = reverse("otp_sms")
        self.headers = {'Authorization': f'Bearer {self.token}'}

    def test_send_sms_to_valid_num(self):
        data = {"user_num": "+543415153601"}
        response = self.client.get(
            self.otp_sms, headers=self.headers, data=data)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_send_sms_to_invalid_num(self):

        data = {"user_num": "+542"}
        response = self.client.get(
            self.otp_sms, headers=self.headers, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get("msg"), "Invalid field 'Phone': Invalid phone number.")
        

    def test_send_sms_to_valid_num_and_check_wrong_otp(self):

        data = {"user_num": "+543415153601"}
        response = self.client.get(
            self.otp_sms, headers=self.headers, data=data)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        data = {"user_num": "+543415153601",
                "otp_code": "34157F"}
        response = self.client.post(
            self.otp_sms, headers=self.headers, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get("msg"), "Invalid field 'Code': Invalid code.")

        

    def test_send_sms_to_already_verified_num(self):
        self.user.verified = True
        self.user.save()

        data = {"user_num": "+543415153601"}
        response = self.client.get(
            self.otp_sms, headers=self.headers, data=data)
        self.assertEqual(response.data.get("msg"), "Invalid field 'Number': User already verified.")


    def test_check_otp_to_already_verified_num(self):
        self.user.verified = True
        self.user.save()

        data = {"user_num": "+543415153601",
                "otp_code": "34157F"}
        response = self.client.post(
            self.otp_sms, headers=self.headers, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get("msg"), "Invalid field 'Number': User already verified.")


"""
