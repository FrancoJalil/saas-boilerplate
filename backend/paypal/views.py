from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import IsAuthenticated

from .serializers import OrderSerializer, OnSuccessSerializer
from helpers.handle_errors import raise_400_HTTP_if_serializer_invalid
from .services import capture_paypal_payment, process_completed_payment, create_paypal_order
from user.permissions import IsVerifiedPermission
from .models import Purchase
from .serializers import PurchaseSerializer

@api_view(['POST'])
@permission_classes([IsAuthenticated, IsVerifiedPermission])
def create_order(request):
    """
   Create a custom order using PayPal.

   Request Body:
       cart (list):
           - id (str): The PayPal ID of the product.
           - value (float): The value or price of the product.

   Returns:
       Response:
           - 200 OK: The PayPal order creation response data.
           - 400 Bad Request:
               - If the user's account is not verified.
               - If the requested product does not exist.
               - If there is an error during the PayPal order creation process.

   Raises:
       PaypalProductModel.DoesNotExist: If the requested product does not exist.
   """

    user = request.user
    serializer = OrderSerializer(
        data=request.data, context={"user": user})
    
    raise_400_HTTP_if_serializer_invalid(serializer)
    product, value = serializer.validated_data.get("cart")

    try:
        order_data = create_paypal_order(user, product, value)
    except Exception as e:
        print(str(e))
        return Response({"msg": "Unexpected error."}, status=400)

    return Response(order_data)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsVerifiedPermission])
def capture_order(request):
    """
    Handle the success response from PayPal after a custom order.

    Request Body:
        - orderID (str): The order ID from the PayPal response.
        - Other data from the PayPal response.

    Returns:
        Response:
            - 200 OK: The PayPal capture response data.
            - 400 Bad Request: If there is an error during the payment capture process.

    Steps:
        1. Retrieve the user from the request.
        2. Extract the order ID from the PayPal response.
        3. Generate a PayPal access token.
        4. Capture the PayPal payment using the order ID.
        5. Process the capture response:
            - If the payment status is 'COMPLETED':
                - If the reference is 'CUSTOM' (custom token purchase):
                    - Calculate the number of tokens purchased.
                    - Add the tokens to the user's account.
                    - Send an email notification to the user.
                - Save the user's updated token balance.
                - Create a Purchase record with the user, product, and price.
            - If there is an exception, return an error response.
        6. Return the PayPal capture response.
    """

    serializer = OnSuccessSerializer(data=request.data)
    raise_400_HTTP_if_serializer_invalid(serializer)
    order_id = serializer.validated_data.get("orderID")


    try:
        capture_response = capture_paypal_payment(order_id)
    except Exception as e:
        print(str(e))
        return Response({"msg": "Paypal unexpected error."}, status=400)

    if capture_response['status'] == 'COMPLETED':
        process_completed_payment(request.user, capture_response)

    return Response(status=201)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsVerifiedPermission])
def purchases(request):

    user = request.user
    user_purchases = Purchase.objects.filter(
        user=user).order_by('-purchased_date')
    paginator = PageNumberPagination()
    paginator.page_size = request.GET.get('page_size', 5)
    user_purchases_page = paginator.paginate_queryset(user_purchases, request)

    product_fields = ['name']

    serializer = PurchaseSerializer(user_purchases_page, many=True, context={
                                    'product_fields': product_fields})

    return paginator.get_paginated_response(
        {
            "user_purchases": serializer.data,
            "total_pages": paginator.page.paginator.num_pages
        }
    )

