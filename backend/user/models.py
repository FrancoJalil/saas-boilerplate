from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from helpers.email import send_email

from django.utils import timezone
import string
import secrets

from django.db.models.signals import post_save
from django.dispatch import receiver


class OtpCode(models.Model):
    GOOGLE = 'google'
    EMAIL = 'email'
    CHANGE_PASSWORD = 'change_password'
    ACTION_TYPES = [
        (GOOGLE, 'Google'),
        (EMAIL, 'Email'),
        (CHANGE_PASSWORD, 'Change Password'),
    ]

    email = models.EmailField()
    otp = models.CharField(max_length=6, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expiry_date = models.DateTimeField(blank=True, null=True)
    action_type = models.CharField(max_length=20, choices=ACTION_TYPES)

    def __str__(self):
        return f"{self.email} | {self.action_type}"

    def is_expired(self):
        return timezone.now() >= self.expiry_date

    def generate_and_send_otp(self):
        # Generar código de confirmación
        minutes_expire = 10
        otp = ''.join(secrets.choice(string.digits) for _ in range(6))
        expiry_date = timezone.now() + timezone.timedelta(minutes=minutes_expire)
        self.otp = otp
        self.expiry_date = expiry_date
        self.save()

        sent = send_email("OTP", self.email, context={
            "email": self.email,
            "otp": self.otp})


       
        return sent

    def validate_otp(self, code, action_type, delete_otp=False):
        
        if action_type == self.action_type:
            if self.otp == code and not self.is_expired():
                
                if delete_otp:
                    self.delete()
                
                return True, None
            return False, "Invalid or expired code."

        return False, "Code not generated yet."

        # if access google corresponde con el email guardado en OTP

    def validate_google_credential(self, google_credential, action_type):

        if action_type == self.action_type:
            from .helpers.auth import check_google_credentials
            valid = check_google_credentials(google_credential)
            if not valid:
                return False, "Invalid Google credentials."
            return True, None

        return False, "Code not generated yet."



class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required.')

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)

        # Configurar la contraseña usando el método set_password
        user.set_password(password)

        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):

    email = models.EmailField(unique=True)
    password = models.CharField(max_length=200)
    num = models.CharField(max_length=30, unique=True, null=True, blank=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    picture = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    paypal_id = models.CharField(max_length=500, blank=True, null=True)
    tokens = models.IntegerField(null=True, blank=True, default=0)
    verified = models.BooleanField(default=False)
    premium = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    def change_password(self, user, new_password):
        # Custom password validation
        if len(new_password) < 8:
            raise ValueError('Password must be at least 8 characters.')

        has_letter = any(char.isalpha() for char in new_password)
        has_digit = any(char.isdigit() for char in new_password)

        if not (has_letter and has_digit):
            raise ValueError(
                'The password must contain at least one letter and one number.')

        try:
            # Intentar establecer la nueva contraseña
            user.set_password(new_password)
        except Exception as e:
            # Manejar la excepción según sea necesario
            raise ValueError(f'Error setting password: Try again later.')

        user.save()


class UserPreferences(models.Model):

    LANGUAGE_CHOICES = [
        ('ES', 'Español'),
        ('EN', 'Inglés'),
    ]

    language = models.CharField(
        max_length=2, choices=LANGUAGE_CHOICES, default='EN')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.email


class WhitelistData(models.Model):

    email = models.CharField(max_length=200)
    date_joined = models.DateTimeField(auto_now_add=True)

@receiver(post_save, sender=CustomUser)
def create_user_utils_models(sender, instance, created, **kwargs):
    if created:

        OtpCode.objects.get_or_create(email=instance.email)
        UserPreferences.objects.create(user=instance)
