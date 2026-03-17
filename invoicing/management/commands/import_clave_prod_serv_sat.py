import pandas as pd
from django.core.management.base import BaseCommand
from django.db import transaction

from invoicing.models.sat import ClaveProdServ
# Reemplaza 'invoicing' por el nombre real de tu app en Django si es diferente


class Command(BaseCommand):
    help = 'Importa el catálogo c_ClaveProdServ del SAT desde un archivo Excel hacia PostgreSQL'

    def add_arguments(self, parser):
        parser.add_argument(
            'ruta_excel', 
            type=str, 
            help='Ruta absoluta o relativa al archivo Excel del SAT'
        )

    def handle(self, *args, **options):
        ruta_archivo = options['ruta_excel']
        self.stdout.write(self.style.WARNING(f"Iniciando lectura del archivo: {ruta_archivo}..."))

        try:
            # Leer el Excel especificando la hoja, saltando las primeras 4 filas (para iniciar en la 5)
            # y usando explícitamente las columnas A(0), B(1), C(2), D(3) e I(8)
            df = pd.read_excel(
                ruta_archivo,
                sheet_name='c_ClaveProdServ',
                skiprows=4,
                usecols=[0, 1, 2, 3, 8], 
                names=['clave', 'descripcion', 'iva', 'ieps', 'palabras_similares'],
                dtype={'clave': str} # Forzar que la clave sea texto para no perder ceros a la izquierda
            )

            # Limpiar datos: eliminar filas donde la clave esté vacía (NaN)
            df = df.dropna(subset=['clave'])

            registros_a_crear = []
            
            self.stdout.write(self.style.WARNING("Procesando datos en memoria..."))

            for index, row in df.iterrows():
                # Extraer y limpiar cada campo, manejando los valores nulos (NaN) de Pandas
                clave = str(row['clave']).strip()[:8]
                descripcion = str(row['descripcion']).strip() if pd.notna(row['descripcion']) else ''
                iva = str(row['iva']).strip() if pd.notna(row['iva']) else None
                ieps = str(row['ieps']).strip() if pd.notna(row['ieps']) else None
                similares = str(row['palabras_similares']).strip() if pd.notna(row['palabras_similares']) else None

                # Crear la instancia del modelo (aún no se guarda en la BD)
                registros_a_crear.append(
                    ClaveProdServ(
                        clave=clave,
                        descripcion=descripcion,
                        incluir_iva_trasladado=iva,
                        incluir_ieps_trasladado=ieps,
                        palabras_similares=similares
                    )
                )

            total_registros = len(registros_a_crear)
            self.stdout.write(self.style.SUCCESS(f"Se prepararon {total_registros} registros. Insertando en PostgreSQL..."))

            # Guardar en base de datos usando bulk_create en lotes de 5000
            # ignore_conflicts=True evita que el script falle si lo corres dos veces y ya existen las claves
            with transaction.atomic():
                ClaveProdServ.objects.bulk_create(
                    registros_a_crear, 
                    batch_size=5000, 
                    ignore_conflicts=True 
                )

            self.stdout.write(self.style.SUCCESS("¡Importación masiva completada con éxito!"))

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"Error: No se encontró el archivo en la ruta {ruta_archivo}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Ocurrió un error inesperado: {str(e)}"))