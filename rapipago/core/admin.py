from django.contrib import admin
from .models import Invoice, Customer


class InvoiceInlineAdmin(admin.TabularInline):
    model = Invoice
    readonly_fields = ['external_id', 'payment_id',  'creation_date', 'expiration_date',
                       'payment_date', 'barcode', 'amount', 'extra_data', 'status']
    extra = 0
    can_delete = False

    def has_add_permission(self, request, obj):
        return False


class InvoiceAdmin(admin.ModelAdmin):
    search_fields = ['external_id', 'customer__external_id']
    list_display = ['external_id', 'customer', 'payment_id',  'creation_date', 'expiration_date',
                    'payment_date', 'barcode', 'amount', 'extra_data', 'status']

    can_delete = False
    def has_add_permission(self, obj):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

class CustomerAdmin(admin.ModelAdmin):
    list_display = ['external_id', 'name', 'last_name']
    inlines = [InvoiceInlineAdmin]
    search_fields = ['external_id', 'invoices__external_id']

    def has_add_permission(self, obj):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(Customer, CustomerAdmin)
admin.site.register(Invoice, InvoiceAdmin)
