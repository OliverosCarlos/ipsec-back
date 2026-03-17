from django.db import models
from django.contrib.postgres.indexes import GinIndex

class SatCatalog(models.Model):
	"""
	Catálogo SAT genérico para normalizar valores del Anexo 20 (CFDI 4.0),
	p.ej.: c_RegimenFiscal, c_Pais, c_Banco, c_Moneda, c_ClaveProdServ, etc.
	Mantén las vigencias para evitar usar claves fuera de periodo.
	Fuentes: Catálogos CFDI 4.0 (SAT / Anexo 20).
	"""
	code = models.CharField(max_length=20, primary_key=True)
	catalog = models.CharField(max_length=60, db_index=True)
	description = models.CharField(max_length=255)
	valid_from = models.DateField(null=True, blank=True)
	valid_to = models.DateField(null=True, blank=True)

	class Meta:
		indexes = [models.Index(fields=['catalog', 'code'])]
		verbose_name = 'Catálogo SAT'
		verbose_name_plural = 'Catálogos SAT'

	def __str__(self):
		return f'{self.catalog}:{self.code} - {self.description}'


class ClaveProdServ(models.Model):
    clave = models.CharField(
        max_length=8, 
        primary_key=True,
        help_text="Clave de 8 dígitos proporcionada por el SAT"
    )
    descripcion = models.TextField(
        help_text="Descripción oficial del producto o servicio"
    )
    incluir_iva_trasladado = models.CharField(
        max_length=10, 
        null=True, 
        blank=True,
        help_text="Indicador de IVA trasladado (Ej. 'Sí', 'No', 'Opcional')"
    )
    incluir_ieps_trasladado = models.CharField(
        max_length=10, 
        null=True, 
        blank=True,
        help_text="Indicador de IEPS trasladado"
    )
    palabras_similares = models.TextField(
        null=True, 
        blank=True,
        help_text="Palabras clave para facilitar la búsqueda en el ERP"
    )

    class Meta:
        db_table = 'sat_claveprodserv'
        verbose_name = 'Clave Producto/Servicio SAT'
        verbose_name_plural = 'Claves Productos/Servicios SAT'
        indexes = [
            # Índice GIN usando la extensión pg_trgm de PostgreSQL
            GinIndex(
                name='clave_desc_gin_idx',
                fields=['descripcion'], 
                opclasses=['gin_trgm_ops']
            )
        ]

    def __str__(self):
        return f"{self.clave} - {self.descripcion}"


class ClaveUnidad(models.Model):
    clave = models.CharField(
        max_length=10,
        primary_key=True,
        help_text="Clave de unidad proporcionada por el SAT"
    )
    name = models.CharField(
        max_length=255,
        help_text="Nombre de la unidad de medida"
    )

    class Meta:
        db_table = 'sat_claveunidad'
        verbose_name = 'Clave Unidad SAT'
        verbose_name_plural = 'Claves Unidades SAT'
        indexes = [
            GinIndex(
                name='claveunidad_name_gin_idx',
                fields=['name'],
                opclasses=['gin_trgm_ops']
            )
        ]

    def __str__(self):
        return f"{self.clave} - {self.name}"

