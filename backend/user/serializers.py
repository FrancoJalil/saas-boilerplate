from rest_framework import serializers
from .models import OtpCode, CustomUser, UserPreferences
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate
from .helpers.sms import send_sms, verify_otp_sms
from django.core.validators import EmailValidator
from .helpers.validators import is_not_registered, is_registered, validate_password, validate_register_type
from helpers.email import send_email

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['email'] = user.email

        return token


class PasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(
        min_length=8, validators=[validate_password], label="New Password")


class OTPCodeSignUpSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        validators=[EmailValidator(), is_not_registered], label="Email")
    otp = serializers.CharField(required=False, label="Code")

    class Meta:
        model = OtpCode
        fields = ('email', 'otp')


class EmailSerializer(serializers.Serializer):
    email = serializers.EmailField(label="Email")


class EmailExistsSerializer(serializers.Serializer):
    email = serializers.EmailField(
        validators=[EmailValidator(), is_registered], label="Email")


class CustomUserStatusSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(label="Email")
    verified = serializers.BooleanField(label="Verified")
    premium = serializers.BooleanField(label="Premium")
    tokens = serializers.IntegerField(label="Tokens")

    class Meta:
        model = CustomUser
        fields = ('email', 'verified', 'premium', 'tokens')


class UserPreferencesSerializer(serializers.ModelSerializer):
    language = serializers.ChoiceField(choices=UserPreferences.LANGUAGE_CHOICES, label="Language")
    
    class Meta:
        model = UserPreferences
        fields = 'language'


class RegisterEmailSerializer(serializers.Serializer):

    email = serializers.EmailField(validators=[is_not_registered], label="Email")
    password = serializers.CharField(validators=[validate_password], label="Password")
    otp = serializers.CharField(required=False, allow_blank=True, allow_null=True, label="Code")
    google_credential = serializers.CharField(required=False, allow_blank=True, allow_null=True, label="Google Auth")
    register_type = serializers.CharField(validators=[validate_register_type], label="Type of register")

    def validate(self, data):
        otp = data.get('otp')
        google_credential = data.get('google_credential')

        if not otp and not google_credential:
            raise serializers.ValidationError('Either otp or google_credential is required.')

        return data

    def create(self, validated_data):
        email = validated_data['email']
        password = validated_data['password']

        CustomUser.objects.create_user(email=email, password=password)

        user_authenticated = authenticate(email=email, password=password)
        tokens = MyTokenObtainPairSerializer().get_token(user_authenticated)

        # send welcome email
        send_email("register", email, context={
            "email": email})


        return {
            'refresh': str(tokens),
            'access': str(tokens.access_token),
            'is_new_user': True
        }


class CustomUserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(label="Email")
    password = serializers.CharField(label="Password")
    class Meta:
        model = CustomUser
        fields = ("email", "password")


class OTPForgotSerializer(serializers.Serializer):
    email = serializers.EmailField(
        validators=[EmailValidator(), is_registered], label="Email")
    otp = serializers.CharField(required=False, label="Code")


class ChangePasswordForgotSerializer(OTPForgotSerializer, PasswordSerializer):

    pass


class UserDataSerializer(serializers.ModelSerializer):
    
    email = serializers.EmailField(label="Email")
    tokens = serializers.IntegerField(label="Tokens")
    verified = serializers.BooleanField(label="Verified")
    num = serializers.IntegerField(label="Phone")
    date_joined = serializers.DateTimeField(label="Date Joined")

    class Meta:
        model = CustomUser
        fields = ['email', 'tokens', 'verified', 'num', 'date_joined']

    def get_fields(self):
        fields = super().get_fields()
        requested_fields = self.context.get('requested_fields', None)

        if requested_fields:
            allowed = set(requested_fields)
            existing = set(fields.keys())
            for field_name in allowed - existing:
                raise serializers.ValidationError(
                    f"The field '{field_name}' is not a valid field for the CustomUser model.")

            for field_name in existing - allowed:
                fields.pop(field_name)

        return fields


class GoogleAuthRequestSerializer(serializers.Serializer):
    userInfo = serializers.DictField(label="Google permissions")

    def validate(self, data):
        if 'credential' not in data['userInfo'] and 'access_token' not in data['userInfo']:
            raise serializers.ValidationError(
                "Missing credential or access_token in userInfo")
        return data


class ContactMeSerializer(serializers.Serializer):
    subject = serializers.CharField(max_length=100, label="Subject")
    msg = serializers.CharField(max_length=1000, label="Message")

    
class NumberSerializer(serializers.Serializer):
    user_num = serializers.CharField(max_length=20, label="Phone")

    def validate(self, data):
        user = self.context.get("user")
        custom_user = CustomUser.objects.get(id=user.id)
        user_num = data.get('user_num')
        

        if CustomUser.objects.filter(num=user_num).exists():
            raise serializers.ValidationError("Num already verified.")

        if custom_user.verified:
            raise serializers.ValidationError("User already verified.")
        
        return user_num


class OTPSendSMSSerializer(NumberSerializer):

    def validate(self, data):
        user_num = super().validate(data)
        
        verification = send_sms(user_num)
        if not verification:
            raise serializers.ValidationError("Invalid phone number.")

        
        return data


class OTPSMSVerificationSerializer(NumberSerializer):
    otp_code = serializers.CharField(max_length=6, required=True, label="Code")
        
    def validate(self, data):
        user_num = super().validate(data)

        user = self.context['user']
        
        otp_code = data.get('otp_code')

        status = verify_otp_sms(otp_code, user_num)
        if status != 'approved':
            raise serializers.ValidationError("Invalid code.")
        
        user = self.context.get("user")
        custom_user = CustomUser.objects.get(id=user.id)
        
        custom_user.num = user_num
        custom_user.verified = True
        custom_user.save()

        return data
    

