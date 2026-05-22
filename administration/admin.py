from django.contrib import admin

from .models import (
    Company, CompanyAddress, CompanyContact,
    CompanyBankAccount, CompanyCertificate,
)


class CompanyAddressInline(admin.TabularInline):
    model = CompanyAddress
    extra = 0


class CompanyContactInline(admin.TabularInline):
    model = CompanyContact
    extra = 0


class CompanyBankAccountInline(admin.TabularInline):
    model = CompanyBankAccount
    extra = 0


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('legal_name', 'rfc', 'person_type', 'country')
    search_fields = ('legal_name', 'rfc', 'commercial_name')
    inlines = [CompanyAddressInline, CompanyContactInline, CompanyBankAccountInline]

    def has_add_permission(self, request):
        if Company.objects.exists():
            return False
        return super().has_add_permission(request)


@admin.register(CompanyCertificate)
class CompanyCertificateAdmin(admin.ModelAdmin):
    list_display = ('serial_number', 'company', 'valid_from', 'valid_to', 'is_default')
    search_fields = ('serial_number',)
