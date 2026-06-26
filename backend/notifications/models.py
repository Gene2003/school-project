"""A log of every SMS / email the platform sends (or simulates)."""

from django.conf import settings
from django.db import models


class Notification(models.Model):
    class Channel(models.TextChoices):
        SMS = 'sms', 'SMS'
        EMAIL = 'email', 'Email'

    class Status(models.TextChoices):
        SENT = 'sent', 'Sent'
        SIMULATED = 'simulated', 'Simulated'
        FAILED = 'failed', 'Failed'

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='notifications',
    )
    channel = models.CharField(max_length=8, choices=Channel.choices)
    to = models.CharField(max_length=255)
    subject = models.CharField(max_length=255, blank=True)
    message = models.TextField()
    status = models.CharField(max_length=10, choices=Status.choices)
    provider_response = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.channel} to {self.to} ({self.status})'
