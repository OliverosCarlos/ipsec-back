from django.contrib import admin

from .models import PersonTitle, CompanySector


@admin.register(PersonTitle)
class PersonTitleAdmin(admin.ModelAdmin):
	list_display = ['code', 'name', 'abbreviation', 'is_active']
	list_filter = ['is_active']
	search_fields = ['code', 'name', 'abbreviation']


@admin.register(CompanySector)
class CompanySectorAdmin(admin.ModelAdmin):
	list_display = ['code', 'name', 'is_active']
	list_filter = ['is_active']
	search_fields = ['code', 'name', 'description']
