"""Payment initialization and verification (Paystack)."""

import logging
import uuid

from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from orders.models import Order

from . import services
from .models import Transaction
from .serializers import (
    InitializePaymentSerializer,
    TransactionSerializer,
    VerifyPaymentSerializer,
)

logger = logging.getLogger(__name__)


class InitializePaymentView(APIView):
    """POST /api/payments/initialize/ — start payment for a pending order."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = InitializePaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        order = get_object_or_404(
            Order, id=serializer.validated_data['order_id'], buyer=request.user
        )
        if order.status == Order.Status.PAID:
            return Response({'detail': 'Order is already paid.'},
                            status=status.HTTP_400_BAD_REQUEST)

        reference = f'AGRIC-{uuid.uuid4().hex[:12].upper()}'
        transaction = Transaction.objects.create(
            reference=reference,
            order=order,
            user=request.user,
            amount=order.total_amount,
            simulated=not services.is_live(),
        )

        # Build seller split instructions where subaccounts exist (live mode).
        subaccounts = []
        for item in order.items.all():
            code = getattr(item.seller, 'paystack_subaccount', '')
            if code:
                subaccounts.append({
                    'subaccount': code,
                    'share': int(round(float(item.subtotal) * 100)),
                })

        result = services.initialize_transaction(
            email=order.email,
            amount=order.total_amount,
            reference=reference,
            callback_url=f'{request.build_absolute_uri("/")[:-1]}/api/payments/callback/',
            subaccounts=subaccounts or None,
        )

        if not result.get('status'):
            transaction.status = Transaction.Status.FAILED
            transaction.gateway_response = result.get('raw', {})
            transaction.save()
            return Response({'detail': 'Could not initialize payment.'},
                            status=status.HTTP_502_BAD_GATEWAY)

        return Response({
            'authorization_url': result['authorization_url'],
            'reference': reference,
            'simulated': result.get('simulated', False),
            'public_key': settings.PAYSTACK_PUBLIC_KEY,
        })


class VerifyPaymentView(APIView):
    """POST /api/payments/verify/ — confirm a transaction and finalize the order."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = VerifyPaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        reference = serializer.validated_data['reference']

        transaction = get_object_or_404(Transaction, reference=reference, user=request.user)
        result = services.verify_transaction(reference)
        transaction.gateway_response = result.get('raw', {})

        if result['status'] == 'success':
            transaction.status = Transaction.Status.SUCCESS
            transaction.save()
            _finalize_paid_order(transaction)
            return Response({
                'status': 'success',
                'order': transaction.order_id,
                'transaction': TransactionSerializer(transaction).data,
            })

        transaction.status = Transaction.Status.FAILED
        transaction.save()
        return Response({'status': 'failed'}, status=status.HTTP_400_BAD_REQUEST)


def _finalize_paid_order(transaction):
    """Mark the order paid, record commissions, and dispatch notifications once."""
    order = transaction.order
    if order.status == Order.Status.PAID:
        return  # idempotent — already processed

    order.status = Order.Status.PAID
    order.save(update_fields=['status', 'updated_at'])

    # Commission + referral tracking
    try:
        from commissions.services import record_commissions_for_order
        record_commissions_for_order(order)
    except Exception:  # pragma: no cover - never block payment on bookkeeping
        logger.exception('Failed to record commissions for order %s', order.reference)

    # SMS + email confirmations
    try:
        from notifications.services import send_order_confirmation
        send_order_confirmation(order)
    except Exception:  # pragma: no cover
        logger.exception('Failed to send notifications for order %s', order.reference)


class TransactionListView(APIView):
    """GET /api/payments/ — the authenticated user's transaction history."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        qs = Transaction.objects.filter(user=request.user)
        return Response(TransactionSerializer(qs, many=True).data)
