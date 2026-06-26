"""Payment transactions processed through Paystack."""

import uuid

from django.conf import settings
from django.db import models


class Transaction(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        SUCCESS = 'success', 'Success'
        FAILED = 'failed', 'Failed'

    # Paystack expects a unique string reference per transaction.
    reference = models.CharField(max_length=64, unique=True, default=uuid.uuid4)
    order = models.ForeignKey(
        'orders.Order', on_delete=models.CASCADE, related_name='transactions'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='transactions'
    )

    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=8, default='KES')
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)

    # Whether the platform simulated this payment (no live Paystack key present)
    simulated = models.BooleanField(default=False)
    gateway_response = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.reference} — {self.amount} {self.currency} ({self.status})'
