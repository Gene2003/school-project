from django.contrib import admin

from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('channel', 'to', 'subject', 'status', 'created_at')
    list_filter = ('channel', 'status')
    search_fields = ('to', 'subject', 'message')
    readonly_fields = ('provider_response',)
