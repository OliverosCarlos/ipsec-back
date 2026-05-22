from django.contrib import admin

from .models import PersonTitle, CompanySector, Department, EmployeeStatus, Employee


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


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
	list_display = ['code', 'name', 'is_active']
	list_filter = ['is_active']
	search_fields = ['code', 'name']


@admin.register(EmployeeStatus)
class EmployeeStatusAdmin(admin.ModelAdmin):
	list_display = ['code', 'name', 'is_active']
	list_filter = ['is_active']
	search_fields = ['code', 'name']


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
	list_display = ['first_name', 'last_name_father', 'last_name_mother', 'email', 'department', 'job_position', 'is_active']
	list_filter = ['is_active', 'department', 'job_position', 'status']
	search_fields = ['first_name', 'last_name_father', 'last_name_mother', 'email']
