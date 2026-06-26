from django.contrib import admin

from .models import Commission


@admin.register(Commission)
class CommissionAdmin(admin.ModelAdmin):
    list_display = ('order', 'kind', 'beneficiary', 'rate_percent', 'amount', 'created_at')
    list_filter = ('kind', 'created_at')
    search_fields = ('order__reference', 'beneficiary__email')
