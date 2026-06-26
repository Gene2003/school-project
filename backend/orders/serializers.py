"""Order serializers, including nested checkout creation."""

from django.db import transaction
from rest_framework import serializers

from products.models import Product

from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    subtotal = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    seller_name = serializers.CharField(source='seller.full_name', read_only=True)

    class Meta:
        model = OrderItem
        fields = (
            'id', 'product', 'product_name', 'seller', 'seller_name',
            'unit_price', 'quantity', 'subtotal',
        )
        read_only_fields = ('product_name', 'seller', 'unit_price', 'seller_name')


class CheckoutItemSerializer(serializers.Serializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    quantity = serializers.IntegerField(min_value=1)


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    buyer_name = serializers.CharField(source='buyer.full_name', read_only=True)

    class Meta:
        model = Order
        fields = (
            'id', 'reference', 'buyer', 'buyer_name', 'full_name', 'email',
            'phone_number', 'delivery_address', 'total_amount', 'status',
            'status_display', 'items', 'created_at',
        )
        read_only_fields = ('reference', 'buyer', 'total_amount', 'status')


class CheckoutSerializer(serializers.Serializer):
    """Validate a cart and create a pending order with snapshot line items."""

    full_name = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    phone_number = serializers.CharField(max_length=20, required=False, allow_blank=True)
    delivery_address = serializers.CharField(max_length=255, required=False, allow_blank=True)
    items = CheckoutItemSerializer(many=True)

    def validate_items(self, items):
        if not items:
            raise serializers.ValidationError('Your cart is empty.')
        for entry in items:
            product = entry['product']
            if not product.is_active:
                raise serializers.ValidationError(f'"{product.name}" is no longer available.')
            if entry['quantity'] > product.quantity_available:
                raise serializers.ValidationError(
                    f'Only {product.quantity_available} {product.get_unit_display()}(s) '
                    f'of "{product.name}" are in stock.'
                )
        return items

    @transaction.atomic
    def create(self, validated_data):
        items = validated_data.pop('items')
        buyer = self.context['request'].user

        order = Order.objects.create(buyer=buyer, **validated_data)
        for entry in items:
            product = entry['product']
            quantity = entry['quantity']
            OrderItem.objects.create(
                order=order,
                product=product,
                product_name=product.name,
                seller=product.seller,
                unit_price=product.price,
                quantity=quantity,
            )
            # Reserve stock immediately.
            product.quantity_available -= quantity
            product.save(update_fields=['quantity_available'])

        order.recalculate_total()
        order.save(update_fields=['total_amount'])
        return order
