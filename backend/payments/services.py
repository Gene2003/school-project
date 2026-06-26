"""
Thin Paystack client.

When PAYSTACK_SECRET_KEY is configured the real Paystack API is called.
Otherwise the platform runs in *simulation mode*: it returns deterministic,
well-formed responses so the whole checkout flow can be exercised end-to-end
during development and demos without live keys.
"""

import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)

PAYSTACK_BASE_URL = 'https://api.paystack.co'


def is_live():
    return bool(settings.PAYSTACK_SECRET_KEY)


def _headers():
    return {
        'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}',
        'Content-Type': 'application/json',
    }


def initialize_transaction(*, email, amount, reference, callback_url=None, subaccounts=None):
    """
    Start a transaction. `amount` is in the major currency unit (e.g. KES);
    Paystack works in the smallest unit (kobo/cents), so we multiply by 100.

    `subaccounts` is an optional list of {"subaccount": code, "share": amount}
    used for split payments to sellers.
    """
    amount_minor = int(round(float(amount) * 100))

    if not is_live():
        # Simulation: the frontend will redirect to our own mock pay page.
        authorization_url = (
            f'{settings.FRONTEND_URL}/pay/simulate?reference={reference}'
        )
        logger.info('Paystack SIMULATION init: ref=%s amount=%s', reference, amount)
        return {
            'simulated': True,
            'status': True,
            'authorization_url': authorization_url,
            'reference': reference,
        }

    payload = {
        'email': email,
        'amount': amount_minor,
        'reference': reference,
        'currency': 'KES',
    }
    if callback_url:
        payload['callback_url'] = callback_url
    if subaccounts:
        payload['split'] = {'type': 'flat', 'subaccounts': subaccounts}

    resp = requests.post(
        f'{PAYSTACK_BASE_URL}/transaction/initialize',
        json=payload, headers=_headers(), timeout=20,
    )
    data = resp.json()
    body = data.get('data', {})
    return {
        'simulated': False,
        'status': data.get('status', False),
        'authorization_url': body.get('authorization_url'),
        'reference': body.get('reference', reference),
        'raw': data,
    }


def verify_transaction(reference):
    """Confirm whether a transaction succeeded."""
    if not is_live():
        logger.info('Paystack SIMULATION verify: ref=%s -> success', reference)
        return {
            'simulated': True,
            'status': 'success',
            'raw': {'data': {'status': 'success', 'reference': reference}},
        }

    resp = requests.get(
        f'{PAYSTACK_BASE_URL}/transaction/verify/{reference}',
        headers=_headers(), timeout=20,
    )
    data = resp.json()
    gateway_status = data.get('data', {}).get('status', 'failed')
    return {
        'simulated': False,
        'status': gateway_status,
        'raw': data,
    }
