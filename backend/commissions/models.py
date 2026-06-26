"""Commission ledger: platform fees and referral payouts per order."""

from django.conf import settings
from django.db import models


class Commission(models.Model):
    class Kind(models.TextChoices):
        PLATFORM = 'platform', 'Platform fee'
        REFERRAL = 'referral', 'Referral payout'

    order = models.ForeignKey(
        'orders.Order', on_delete=models.CASCADE, related_name='commissions'
    )
    # The user the commission relates to:
    #  - platform fee: the seller whose sale was charged
    #  - referral payout: the promoter who referred the buyer
    beneficiary = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='commissions', null=True, blank=True,
    )
    kind = models.CharField(max_length=12, choices=Kind.choices)
    rate_percent = models.DecimalField(max_digits=5, decimal_places=2)
    base_amount = models.DecimalField(max_digits=12, decimal_places=2)
    amount = models.DecimalField(max_digits=12, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.get_kind_display()} {self.amount} on order {self.order_id}'
