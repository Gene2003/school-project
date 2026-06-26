"""Commission calculation triggered when an order is paid."""

import logging
from decimal import ROUND_HALF_UP, Decimal

from django.conf import settings

from .models import Commission

logger = logging.getLogger(__name__)


def _pct(amount, percent):
    value = Decimal(str(amount)) * Decimal(str(percent)) / Decimal('100')
    return value.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def record_commissions_for_order(order):
    """
    Create the commission ledger entries for a paid order.

    - A platform fee per seller line item (PLATFORM_COMMISSION_PERCENT).
    - A referral payout to the buyer's referrer, if any
      (REFERRAL_COMMISSION_PERCENT of the order total).

    Idempotent: does nothing if commissions already exist for the order.
    """
    if order.commissions.exists():
        return []

    created = []
    platform_rate = settings.PLATFORM_COMMISSION_PERCENT

    for item in order.items.all():
        fee = _pct(item.subtotal, platform_rate)
        created.append(Commission.objects.create(
            order=order,
            beneficiary=item.seller,
            kind=Commission.Kind.PLATFORM,
            rate_percent=platform_rate,
            base_amount=item.subtotal,
            amount=fee,
        ))

    referrer = getattr(order.buyer, 'referred_by', None)
    if referrer:
        referral_rate = settings.REFERRAL_COMMISSION_PERCENT
        payout = _pct(order.total_amount, referral_rate)
        created.append(Commission.objects.create(
            order=order,
            beneficiary=referrer,
            kind=Commission.Kind.REFERRAL,
            rate_percent=referral_rate,
            base_amount=order.total_amount,
            amount=payout,
        ))

    logger.info('Recorded %s commission entries for order %s', len(created), order.reference)
    return created
