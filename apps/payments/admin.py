from django.contrib import admin
from .models import MockPayment


@admin.register(MockPayment)
class MockPaymentAdmin(admin.ModelAdmin):
    list_display = ("transaction_id", "order", "user", "amount", "status", "created_at")
    list_filter = ("status", "card_brand", "created_at")
    search_fields = ("transaction_id", "order__order_number", "user__email")
    readonly_fields = ("public_id", "transaction_id", "created_at", "updated_at")
