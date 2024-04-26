from django.urls import path
from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


urlpatterns = [

    # AUTH
    path('auth/email/', views.continue_with_email, name="continue_with_email"),
    path('auth/google/', views.continue_with_google, name='continue_with_google'),
    path('auth/credentials/', TokenObtainPairView.as_view(), name='auth_credentials'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='auth_refresh'),

    # SIGNUP
    path('signup/otp', views.check_otp_signup, name="check_otp_signup"),
    path('signup/', views.register_email, name="register"),

    # VERIFICATIONS
    path("verifications/otp/sms/", views.otp_sms, name="otp_sms"),

    # PASSWORD RESETS
    path('passwords/resets/otp/', views.otp_change_password, name="otp_change_password"),
    path('passwords/resets/', views.change_password, name="change_password"),

    # Users
    path('me/', views.user_data, name="user_data"),

    # Utilites
    path("contact/", views.contact_me, name="contact"),

]




