# serializers.py
from rest_framework import serializers
from .models import Purchase, PaypalProductModel


class PaypalProductModelSerializer(serializers.ModelSerializer):
    paypal_id_product = serializers.CharField(label="Product id")
    class Meta:
        model = PaypalProductModel
        fields = ['paypal_id_product']


class NamePaypalProductModelSerializer(serializers.ModelSerializer):
    name = serializers.CharField(label="Product name")
    class Meta:
        model = PaypalProductModel
        fields = ['name']


class PurchaseSerializer(serializers.ModelSerializer):

    user_email = serializers.EmailField(source='user.email', read_only=True, label="email")
    product = NamePaypalProductModelSerializer()

    # 'YYYY-MM-DD'
    purchased_date = serializers.DateTimeField(
        format="%Y-%m-%d", read_only=True)

    class Meta:
        model = Purchase
        fields = ['user_email', 'product', 'purchased_date', 'price', 'id']


class OrderSerializer(serializers.Serializer):
    cart = serializers.ListField(
        child=serializers.DictField(
            child=serializers.CharField()
        ),
    label="Cart")

    def validate_cart(self, cart):
        if not cart:
            raise serializers.ValidationError("Cart cannot be empty.")

        for item in cart:
            if 'id' not in item or 'value' not in item:
                raise serializers.ValidationError(
                    "Invalid cart item. Must contain 'id' and 'value' keys.")

            product_id = item['id']
            value = item['value']  # IF VALUE NOT IN PRECIOS_TOKENS RAISE ERROR

            try:
                value = float(value)
            except ValueError:
                raise serializers.ValidationError(
                    f"Invalid value '{value}' for product '{product_id}'.")

        product = PaypalProductModel.objects.filter(paypal_id_product=product_id).first()
        if not product:
            raise serializers.ValidationError("Product doesn't exist.")

        return product, value



class OnSuccessSerializer(serializers.Serializer):
    orderID = serializers.CharField(required=True, label="Order id")

    def validate(self, attrs):
        orderID = attrs.get('orderID')
        if not orderID:
            raise serializers.ValidationError("orderID is required.")
        return attrs

    def create(self, validated_data):
        # No need to create an instance, as this serializer is used for request data validation only
        return validated_data

    def update(self, instance, validated_data):
        # No need to update an instance, as this serializer is used for request data validation only
        raise NotImplementedError

