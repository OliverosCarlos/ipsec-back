import pandas as pd
from django.core.management.base import BaseCommand
from django.db import transaction

from invoicing.models.sat import ClaveUnidad


class Command(BaseCommand):
    help = 'Importa el catálogo c_ClaveUnidad del SAT desde un archivo Excel hacia PostgreSQL'

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
            # Leer la hoja c_ClaveUnidad, saltando las primeras 6 filas (datos inician en fila 7)
            # Columnas: A(0) = clave, B(1) = name
            df = pd.read_excel(
                ruta_archivo,
                sheet_name='c_ClaveUnidad',
                skiprows=6,
                usecols=[0, 1],
                names=['clave', 'name'],
                dtype={'clave': str}
            )

            # Limpiar datos: eliminar filas donde la clave esté vacía (NaN)
            df = df.dropna(subset=['clave'])

            registros_a_crear = []

            self.stdout.write(self.style.WARNING("Procesando datos en memoria..."))

            for index, row in df.iterrows():
                clave = str(row['clave']).strip()[:10]
                name = str(row['name']).strip() if pd.notna(row['name']) else ''

                registros_a_crear.append(
                    ClaveUnidad(
                        clave=clave,
                        name=name,
                    )
                )

            total_registros = len(registros_a_crear)
            self.stdout.write(self.style.SUCCESS(f"Se prepararon {total_registros} registros. Insertando en PostgreSQL..."))

            with transaction.atomic():
                ClaveUnidad.objects.bulk_create(
                    registros_a_crear,
                    batch_size=5000,
                    ignore_conflicts=True
                )

            self.stdout.write(self.style.SUCCESS("¡Importación masiva completada con éxito!"))

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"Error: No se encontró el archivo en la ruta {ruta_archivo}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Ocurrió un error inesperado: {str(e)}"))
