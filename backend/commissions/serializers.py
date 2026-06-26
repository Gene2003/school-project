from rest_framework import serializers

from .models import Commission


class CommissionSerializer(serializers.ModelSerializer):
    kind_display = serializers.CharField(source='get_kind_display', read_only=True)
    beneficiary_name = serializers.CharField(source='beneficiary.full_name', read_only=True)
    order_reference = serializers.CharField(source='order.reference', read_only=True)

    class Meta:
        model = Commission
        fields = (
            'id', 'order', 'order_reference', 'beneficiary', 'beneficiary_name',
            'kind', 'kind_display', 'rate_percent', 'base_amount', 'amount', 'created_at',
        )
        read_only_fields = fields
