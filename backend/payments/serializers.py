from rest_framework import serializers

from .models import Transaction


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = (
            'id', 'reference', 'order', 'amount', 'currency',
            'status', 'simulated', 'created_at',
        )
        read_only_fields = fields


class InitializePaymentSerializer(serializers.Serializer):
    order_id = serializers.IntegerField()


class VerifyPaymentSerializer(serializers.Serializer):
    reference = serializers.CharField()
