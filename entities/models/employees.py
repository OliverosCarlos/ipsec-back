from django.conf import settings
from django.db import models


class Employee(models.Model):
	"""Datos generales de un empleado."""

	class Gender(models.TextChoices):
		MALE = 'M', 'Masculino'
		FEMALE = 'F', 'Femenino'
		OTHER = 'O', 'Otro'

	first_name = models.CharField('Nombre', max_length=100)
	last_name_father = models.CharField('Apellido paterno', max_length=100)
	last_name_mother = models.CharField('Apellido materno', max_length=100, blank=True, default='')
	date_of_birth = models.DateField('Fecha de nacimiento')
	gender = models.CharField(max_length=1, choices=Gender.choices, blank=True, default='')
	email = models.EmailField('Correo electrónico', blank=True, default='')
	phone = models.CharField('Teléfono', max_length=30, blank=True, default='')
	photo = models.ImageField('Foto de perfil', upload_to='employees/photos/', null=True, blank=True)

	# Relaciones con catálogos
	department = models.ForeignKey(
		'entities.Department',
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
		related_name='employees',
		verbose_name='Departamento',
	)
	job_position = models.ForeignKey(
		'entities.JobPosition',
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
		related_name='employees',
		verbose_name='Puesto',
	)
	status = models.ForeignKey(
		'entities.EmployeeStatus',
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
		related_name='employees',
		verbose_name='Estatus',
	)

	# Vínculo opcional con cuenta de usuario
	account = models.OneToOneField(
		settings.AUTH_USER_MODEL,
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
		related_name='employee',
		verbose_name='Cuenta de usuario',
	)

	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ['last_name_father', 'last_name_mother', 'first_name']
		verbose_name = 'Employee'
		verbose_name_plural = 'Employees'
		indexes = [
			models.Index(fields=['last_name_father', 'last_name_mother']),
			models.Index(fields=['is_active']),
		]

	def __str__(self):
		parts = [self.first_name, self.last_name_father]
		if self.last_name_mother:
			parts.append(self.last_name_mother)
		return ' '.join(parts)

	@property
	def full_name(self):
		return str(self)

	@property
	def age(self):
		import datetime
		today = datetime.date.today()
		born = self.date_of_birth
		return today.year - born.year - ((today.month, today.day) < (born.month, born.day))
