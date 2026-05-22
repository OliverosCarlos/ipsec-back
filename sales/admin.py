from django.contrib import admin

from .models import (
    Quotation, QuotationLine,
    FastSalesProposal, FastQuotation, FastQuotationLine,
)


class QuotationLineInline(admin.TabularInline):
    model = QuotationLine
    extra = 1


@admin.register(Quotation)
class QuotationAdmin(admin.ModelAdmin):
    list_display = ['number', 'partner', 'status', 'date', 'validity_date', 'currency', 'amount_total']
    list_filter = ['status', 'currency', 'date']
    search_fields = ['number', 'partner__legal_name', 'partner__rfc']
    inlines = [QuotationLineInline]


@admin.register(QuotationLine)
class QuotationLineAdmin(admin.ModelAdmin):
    list_display = ['quotation', 'product_service_variation', 'quantity', 'unit_price', 'discount_percent', 'subtotal']
    list_filter = ['quotation__status']


# ── Fast Sales Proposal ────────────────────────────────────────

class FastQuotationInline(admin.TabularInline):
    model = FastQuotation
    extra = 0
    show_change_link = True
    fields = ['description', 'name', 'status', 'date', 'currency', 'amount_total']
    readonly_fields = ['amount_total']


@admin.register(FastSalesProposal)
class FastSalesProposalAdmin(admin.ModelAdmin):
    list_display = ['name', 'partner', 'status', 'salesperson', 'created_at']
    list_filter = ['status']
    search_fields = ['name', 'objective', 'partner__legal_name']
    inlines = [FastQuotationInline]


class FastQuotationLineInline(admin.TabularInline):
    model = FastQuotationLine
    extra = 1


@admin.register(FastQuotation)
class FastQuotationAdmin(admin.ModelAdmin):
    list_display = ['id', 'proposal', 'name', 'description', 'status', 'date', 'currency', 'amount_total']
    list_filter = ['status', 'currency', 'date']
    search_fields = ['name', 'description', 'proposal__name']
    inlines = [FastQuotationLineInline]


@admin.register(FastQuotationLine)
class FastQuotationLineAdmin(admin.ModelAdmin):
    list_display = ['fast_quotation', 'product_service_variation', 'quantity', 'unit_price', 'discount_percent', 'subtotal']
    list_filter = ['fast_quotation__status']
