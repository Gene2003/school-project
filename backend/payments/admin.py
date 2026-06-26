from django.contrib import admin

from .models import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('reference', 'user', 'amount', 'currency', 'status', 'simulated', 'created_at')
    list_filter = ('status', 'simulated', 'currency')
    search_fields = ('reference', 'user__email')
    readonly_fields = ('reference', 'gateway_response')
