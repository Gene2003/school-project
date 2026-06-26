"""Role-based user accounts (farmers, wholesalers, retailers, consumers, admin)."""

import secrets

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    """User manager that uses email as the unique identifier."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('An email address is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', User.Role.ADMIN)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self._create_user(email, password, **extra_fields)


def generate_referral_code():
    """A short, URL-safe referral code for community promoters."""
    return secrets.token_urlsafe(6)


class User(AbstractUser):
    """Custom user identified by email, carrying a marketplace role."""

    class Role(models.TextChoices):
        FARMER = 'farmer', 'Farmer'
        WHOLESALER = 'wholesaler', 'Wholesaler'
        RETAILER = 'retailer', 'Retailer'
        CONSUMER = 'consumer', 'Consumer'
        ADMIN = 'admin', 'Administrator'

    # We authenticate with email, not username.
    username = None
    email = models.EmailField('email address', unique=True)

    full_name = models.CharField(max_length=150, blank=True)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.CONSUMER)
    phone_number = models.CharField(max_length=20, blank=True)
    location = models.CharField(max_length=120, blank=True)

    # Referral / community-promoter tracking
    referral_code = models.CharField(
        max_length=16, unique=True, default=generate_referral_code, editable=False
    )
    referred_by = models.ForeignKey(
        'self', null=True, blank=True, on_delete=models.SET_NULL,
        related_name='referrals',
    )

    # Paystack subaccount code, so split payments can pay sellers directly.
    paystack_subaccount = models.CharField(max_length=64, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return f'{self.full_name or self.email} ({self.role})'

    @property
    def is_seller(self):
        """Farmers and wholesalers can list products for sale."""
        return self.role in {self.Role.FARMER, self.Role.WHOLESALER}
