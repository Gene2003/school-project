"""
Notification dispatch via Africa's Talking (SMS) and SendGrid (email).

Every send is recorded in the Notification log. When the relevant API key is
not configured the message is *simulated*: logged and stored with status
'simulated', so the order flow still completes during development.
"""

import logging

import requests
from django.conf import settings

from .models import Notification

logger = logging.getLogger(__name__)

AT_SMS_URL = 'https://api.africastalking.com/version1/messaging'
SENDGRID_URL = 'https://api.sendgrid.com/v3/mail/send'


def send_sms(to, message, recipient=None):
    """Send an SMS through Africa's Talking, or simulate it."""
    if not to:
        return None

    if not settings.AT_API_KEY:
        logger.info('SMS SIMULATION to %s: %s', to, message)
        return Notification.objects.create(
            recipient=recipient, channel=Notification.Channel.SMS, to=to,
            message=message, status=Notification.Status.SIMULATED,
        )

    try:
        resp = requests.post(
            AT_SMS_URL,
            data={
                'username': settings.AT_USERNAME,
                'to': to,
                'message': message,
                'from': settings.AT_SENDER_ID or None,
            },
            headers={
                'apiKey': settings.AT_API_KEY,
                'Accept': 'application/json',
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            timeout=20,
        )
        return Notification.objects.create(
            recipient=recipient, channel=Notification.Channel.SMS, to=to,
            message=message, status=Notification.Status.SENT,
            provider_response=_safe_json(resp),
        )
    except Exception as exc:  # pragma: no cover
        logger.exception('SMS send failed: %s', exc)
        return Notification.objects.create(
            recipient=recipient, channel=Notification.Channel.SMS, to=to,
            message=message, status=Notification.Status.FAILED,
            provider_response={'error': str(exc)},
        )


def send_email(to, subject, message, recipient=None):
    """Send a transactional email through SendGrid, or simulate it."""
    if not to:
        return None

    if not settings.SENDGRID_API_KEY:
        logger.info('EMAIL SIMULATION to %s | %s | %s', to, subject, message)
        return Notification.objects.create(
            recipient=recipient, channel=Notification.Channel.EMAIL, to=to,
            subject=subject, message=message, status=Notification.Status.SIMULATED,
        )

    try:
        resp = requests.post(
            SENDGRID_URL,
            json={
                'personalizations': [{'to': [{'email': to}]}],
                'from': {'email': settings.DEFAULT_FROM_EMAIL},
                'subject': subject,
                'content': [{'type': 'text/plain', 'value': message}],
            },
            headers={
                'Authorization': f'Bearer {settings.SENDGRID_API_KEY}',
                'Content-Type': 'application/json',
            },
            timeout=20,
        )
        ok = resp.status_code in (200, 201, 202)
        return Notification.objects.create(
            recipient=recipient, channel=Notification.Channel.EMAIL, to=to,
            subject=subject, message=message,
            status=Notification.Status.SENT if ok else Notification.Status.FAILED,
            provider_response={'status_code': resp.status_code},
        )
    except Exception as exc:  # pragma: no cover
        logger.exception('Email send failed: %s', exc)
        return Notification.objects.create(
            recipient=recipient, channel=Notification.Channel.EMAIL, to=to,
            subject=subject, message=message, status=Notification.Status.FAILED,
            provider_response={'error': str(exc)},
        )


def _safe_json(resp):
    try:
        return resp.json()
    except ValueError:
        return {'status_code': resp.status_code, 'text': resp.text[:500]}


def send_order_confirmation(order):
    """Notify the buyer (email + SMS) that their paid order was received."""
    items = ', '.join(f'{i.quantity} x {i.product_name}' for i in order.items.all())
    subject = f'Order {str(order.reference)[:8]} confirmed'
    body = (
        f'Hello {order.full_name},\n\n'
        f'Your payment of KES {order.total_amount} has been received.\n'
        f'Items: {items}\n'
        f'Reference: {order.reference}\n\n'
        f'Thank you for buying directly from local farmers.\n'
        f'— Web-Based Supply Chain Platform'
    )

    send_email(order.email, subject, body, recipient=order.buyer)
    if order.phone_number:
        send_sms(
            order.phone_number,
            f'Order {str(order.reference)[:8]} confirmed. '
            f'Paid KES {order.total_amount}. Thank you!',
            recipient=order.buyer,
        )

    # Let each seller know they have a sale.
    sellers = {}
    for item in order.items.all():
        if item.seller:
            sellers.setdefault(item.seller, []).append(item)
    for seller, seller_items in sellers.items():
        lines = ', '.join(f'{i.quantity} x {i.product_name}' for i in seller_items)
        if seller.phone_number:
            send_sms(seller.phone_number,
                     f'New sale! {lines}. Order {str(order.reference)[:8]}.',
                     recipient=seller)
        if seller.email:
            send_email(seller.email, 'You have a new sale',
                       f'Hello {seller.full_name},\n\nYou sold: {lines}.\n'
                       f'Order reference: {order.reference}.',
                       recipient=seller)
