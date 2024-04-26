
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from helpers.throttling import SimpleRateThrottle
from helpers.handle_errors import get_object_or_404_custom, raise_400_HTTP_if_serializer_invalid
from helpers.email import send_email_to_me

from user.models import CustomUser, OtpCode
from user.models import CustomUser
from .serializers import (ContactMeSerializer, OTPSMSVerificationSerializer, GoogleAuthRequestSerializer, UserDataSerializer, ChangePasswordForgotSerializer,
                          EmailExistsSerializer, OTPForgotSerializer, OTPSendSMSSerializer, RegisterEmailSerializer, OTPCodeSignUpSerializer, EmailSerializer)
from rest_framework import status
from .helpers.auth import get_google_id_info, get_user_tokens


@api_view(['POST'])
@throttle_classes([AnonRateThrottle])
def continue_with_email(request):
    """
    Handle the "continue with email" flow for user signup or login.

    Request Body:
        email (str): The email address to continue with.

    Returns:
        Response:
            - 200 OK:
                {
                    "email_exists": bool
                }
                Indicates if the provided email is already registered or not.
            - 400 Bad Request: If the email sent in the request is invalid according to the serializer.
    """


    serializer = EmailSerializer(data=request.data)
    raise_400_HTTP_if_serializer_invalid(serializer)

    email = serializer.validated_data.get('email')
    email_is_registered = CustomUser.objects.filter(email=email).exists()

    if not email_is_registered:
        otp_email_instance, _ = OtpCode.objects.get_or_create(
            email=email)

        otp_email_instance.action_type = "email"

        generated_and_sent = otp_email_instance.generate_and_send_otp()
        if not generated_and_sent:
            return Response({"msg": "Error sending code."}, status=400)

    return Response({"email_exists": email_is_registered}, status=200)

@throttle_classes([AnonRateThrottle])
@api_view(['POST'])
def check_otp_signup(request):
    """
    Verify the OTP code provided during the signup process.

    Request Body:
        email (str): The email address used for signup.
        otp (str): The one-time password (OTP) code.

    Returns:
        Response:
            - 204 No Content: If the OTP code is valid.
            - 400 Bad Request: If the data sent is invalid according to the serializer.
            - 404 Not Found: If the code has not been generated for the provided email.
    """
    data = request.data
    serializer = OTPCodeSignUpSerializer(data=data)

    raise_400_HTTP_if_serializer_invalid(serializer)

    email = serializer.validated_data.get("email")
    otp = serializer.validated_data.get("otp")

    signup_otp = get_object_or_404_custom(
        OtpCode, email=email, msg="Code not generated yet.")

    is_valid, msg = signup_otp.validate_otp(
        otp, action_type="email")
    if not is_valid:
        return Response({"msg": msg}, status=404)

    return Response(status=204)

@api_view(['POST'])
def register_email(request):
    """
    Register a new user account using an email, OTP code, and password.

    Args:
        request (HttpRequest): The incoming HTTP request.

    Request Body:
        email (str): The email address to register.
        otp (str): The one-time password (OTP) code for verification.
        new_password (str): The new password for the user account.

    Returns:
        Response:
            - 201 Created:
                {
                    "access_token": str,
                    "refresh_token": str
                }
                The authentication tokens for the newly created user account.
            - 400 Bad Request: If the email, OTP code, or new password sent in the request is invalid according to the serializer.
            - 404 Not Found: If the OTP code is invalid or no code has been generated for the provided email.
    """
    serializer = RegisterEmailSerializer(data=request.data)
    raise_400_HTTP_if_serializer_invalid(serializer)
    email = serializer.validated_data.get("email")
    
    signup_otp = get_object_or_404_custom(
        OtpCode, email=email, msg="Code not generated yet.")

    register_type = serializer.validated_data.get("register_type")

    if register_type == "email":
        if signup_otp.action_type == "email":
            otp = serializer.validated_data.get("otp")
            is_valid, msg = signup_otp.validate_otp(
                otp, action_type="email", delete_otp=True)
    
    elif register_type == "google":
        if signup_otp.action_type == "google":
            google_credential = serializer.validated_data.get("google_credential")
            is_valid, msg = signup_otp.validate_google_credential(
                google_credential=google_credential, action_type="google")

    else:
        return Response({"msg": "Code not generated yet."}, status=400)

    if not is_valid:
        return Response({"msg": msg}, status=404)

    tokens = serializer.save()
    return Response(tokens, status=201)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
@throttle_classes([UserRateThrottle])
def otp_sms(request):
    """
    METHOD: GET
        Send a one-time password (OTP) via SMS to the user's phone number for verification.

        Request Params:
            user_num (str): The user's phone number to send the OTP to.

        Returns:
            Response:
                - 204 No Content: If the OTP was sent successfully.
                - 400 Bad Request: If the provided phone number is invalid or the user is already verified.

        Raises:
            serializers.ValidationError:
                - If the user is already verified.
                - If the provided phone number is invalid.
                - If the phone number is already verified for another user.

    METHOD: POST
        Verify the one-time password (OTP) sent via SMS to the authenticated user's phone number.

        Request Body:
            otp_code (str): The OTP code received via SMS.
            user_num (str): The phone-number of the user.

        Returns:
            Response:
                - 204 No Content: If the OTP code is valid and the user's phone number is successfully verified.
                - 400 Bad Request: If the provided OTP code is invalid or the user's phone number is already verified.

        Raises:
            serializers.ValidationError:
                - If the provided OTP code is invalid.
                - If the user's phone number is already verified.
    """

    if request.method == 'GET':
        serializer = OTPSendSMSSerializer(
            data=request.query_params, context={'user': request.user})

        raise_400_HTTP_if_serializer_invalid(serializer)

        return Response(status=204)
    
    elif request.method == 'POST':
        user = request.user
        serializer = OTPSMSVerificationSerializer(
            data=request.data, context={"user": user})

        raise_400_HTTP_if_serializer_invalid(serializer)

        return Response(status=204)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@throttle_classes([SimpleRateThrottle])
def contact_me(request):
    """
    Send a contact message to the system administrator.

    Request Body:
        subject (str): The subject of the message.
        msg (str): The message content.

    Returns:
        Response:
            - 200 OK: If the message was sent successfully.
            - 400 Bad Request:
                - If the provided subject or message is invalid according to the serializer.
                - If an unexpected error occurred while sending the email.

    Raises:
        serializers.ValidationError: If the provided subject or message is invalid according to the serializer.
    """

    serializer = ContactMeSerializer(
        data=request.data, context={'user': request.user})

    raise_400_HTTP_if_serializer_invalid(serializer)

    validated_data = serializer.validated_data
    msg = validated_data.get("msg")
    subject = validated_data.get("subject")
    try:
        send_email_to_me(request.user.email, subject, msg)

    except Exception:
        return Response({'msg': 'Unexpected error, please try again later.'}, status=500)

    return Response(status=200)


@api_view(['POST'])
@throttle_classes([AnonRateThrottle])
def continue_with_google(request):
    """
    Authenticate a user using Google Sign-In or Sign-Up.

    Request Body:
        userInfo (dict): A dictionary containing the user's Google ID token or access token.
            - credential (str): The Google ID token.
            or
            - access_token (str): The Google access token.

    Returns:
        Response:
            - 201 Created:
                {
                    "is_new_user": bool,
                    "email": str
                }
                Returned if the user is new, indicating the user needs to complete the signup process.
            - 204 No Content:
                {
                    "refresh": str,
                    "access": str,
                    "is_new_user": bool
                }
                Returned if the user is already registered, containing the authentication tokens.
            - 400 Bad Request: If the provided userInfo is invalid according to the serializer.
            - 401 Unauthorized: If the Google authentication fails.
            - 500 Internal Server Error: If there is an error generating the authentication tokens.

    Raises:
        serializers.ValidationError: If the provided userInfo is invalid according to the serializer.
    """

    serializer = GoogleAuthRequestSerializer(data=request.data)
    raise_400_HTTP_if_serializer_invalid(serializer)

    idinfo, google_token = get_google_id_info(serializer.validated_data)

    if 'sub' not in idinfo:
        return Response({'error': 'Authentication failed'}, status=401)

    email = idinfo.get('email')
    is_new_user = False

    try:
        user = CustomUser.objects.get(email=email)
    except:
        is_new_user = True
        otp_google_instance, _ = OtpCode.objects.get_or_create(email=email)
        otp_google_instance.action_type = "google"
        otp_google_instance.save()

        return Response({'is_new_user': is_new_user, 'email': email, 'google_token': google_token}, status=201)

    try:
        tokens = get_user_tokens(user)
    except Exception:
        return Response({'msg': 'Failed to generate tokens.'}, status=500)

    return Response({
        'refresh': str(tokens['refresh']),
        'access': str(tokens['access']),
        'is_new_user': is_new_user
    }, status=200)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_data(request):
    """
   Retrieve the authenticated user's data.

   Query Parameters:
       fields (str, optional): A comma-separated list of fields to include in the response.
       /user/data
       /user/data/?fields=email,
       /user/data/?fields=email,num
       ...

   Returns:
       Response:
           - 200 OK:
               {
                   "field1": value,
                   ...
               }
               The requested user data fields.
           - 400 Bad Request: If one or more requested fields are not valid for the CustomUser model.

   Raises:
       serializers.ValidationError: If one or more requested fields are not valid for the CustomUser model.
   """

    fields = request.GET.get('fields')

    requested_fields = fields.split(',') if fields else None

    user = request.user

    try:
        serializer = UserDataSerializer(
            user, context={'requested_fields': requested_fields})
        serialized_data = serializer.data
    except ValidationError as e:
        error_message = e.detail[0]
        return Response({'msg': error_message}, status=status.HTTP_400_BAD_REQUEST)

    return Response(serialized_data)


@api_view(['GET', 'POST'])
@throttle_classes([SimpleRateThrottle])
def otp_change_password(request):
    """
    METHOD: GET
        Send a one-time password (OTP) to the provided email for password reset.

        Request Params:
            email (str): The email address to send the OTP to.

        Returns:
            Response:
                - 204 No Content: If the OTP was generated and sent successfully.
                - 400 Bad Request: If the provided email is invalid or there was an error sending the OTP.

        Raises:
            serializers.ValidationError: If the provided email is invalid.

    METHOD: POST
        Verify the one-time password (OTP) sent via SMS to the authenticated user's phone number.

        Request Body:
            otp_code (str): The OTP code received via SMS.
            user_num (str): The phone-number of the user.

        Returns:
            Response:
                - 204 No Content: If the OTP code is valid and the user's phone number is successfully verified.
                - 400 Bad Request: If the provided OTP code is invalid or the user's phone number is already verified.

        Raises:
            serializers.ValidationError:
                - If the provided OTP code is invalid.
                - If the user's phone number is already verified.
   """
    if request.method == 'GET':
        serializer = EmailExistsSerializer(data=request.query_params)
        raise_400_HTTP_if_serializer_invalid(serializer)
        email = serializer.validated_data.get("email")

        otp_forgot_instance = OtpCode.objects.get(
            email=email)

        otp_forgot_instance.action_type = "change_password"

        generated_and_sent = otp_forgot_instance.generate_and_send_otp()
        if not generated_and_sent:
            return Response({"msg": "Error sending code."}, status=400)

        return Response(status=204)

    elif request.method == 'POST':
        serializer = OTPForgotSerializer(data=request.data)
        raise_400_HTTP_if_serializer_invalid(serializer)

        email = serializer.validated_data.get('email')
        otp = serializer.validated_data.get('otp')

        forgot_otp = get_object_or_404_custom(
            OtpCode, email=email, msg="Code not generated yet.")

        is_valid, msg = forgot_otp.validate_otp(
            otp, action_type="change_password")

        if not is_valid:
            return Response({"msg": msg}, status=400)

        return Response(status=204)


@api_view(['POST'])
@throttle_classes([AnonRateThrottle])
def change_password(request):
    """
   Change the user's password after verifying the OTP for password reset.

   Request Body:
       email (str): The email address for which the OTP was generated.
       otp (str): The one-time password (OTP) code received.
       new_password (str): The new password to set.

   Returns:
       Response:
           - 201 Created:
               {
                   "msg": "Password changed."
               }
               If the password was changed successfully.
           - 400 Bad Request:
               - If the provided email, OTP code, or new password is invalid according to the serializer.
               - If the OTP code is invalid or no code has been generated for the provided email.
               - If there was an error while changing the password.

   Raises:
       serializers.ValidationError: If the provided email, OTP code, or new password is invalid according to the serializer.
   """

    serializer = ChangePasswordForgotSerializer(data=request.data)
    raise_400_HTTP_if_serializer_invalid(serializer)

    email = serializer.validated_data.get("email")
    new_password = serializer.validated_data.get("new_password")
    otp = serializer.validated_data.get("otp")

    forgot_otp = get_object_or_404_custom(
        OtpCode, email=email, msg="Code not generated yet.")

    is_valid, msg = forgot_otp.validate_otp(otp, action_type="change_password", delete_otp=True)

    if not is_valid:
        return Response({"msg": msg}, status=400)

    user = CustomUser.objects.filter(email=email).first()

    try:
        user.change_password(user, new_password)
        return Response({'msg': "Password changed."}, status=201)
    except Exception as e:
        return Response({'msg': str(e)}, status=400)

