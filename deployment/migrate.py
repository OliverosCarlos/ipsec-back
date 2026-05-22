import os
import sys
from pathlib import Path

# Setup Django
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ipsec_back.settings")

import django

django.setup()

from django.core.management import call_command
from django.conf import settings

from deploy_tracker import DeployTracker

STEP_MIGRATE = "migration"
STEP_SUPERUSER = "super_user"


def main():
    db_conf = settings.DATABASES["default"]
    db_name = db_conf["NAME"]
    db_host = db_conf["HOST"]
    db_port = db_conf["PORT"]
    db_user = db_conf["USER"]

    print(f"\nBase de datos: '{db_name}' en {db_host}:{db_port} con usuario '{db_user}'")
    confirm = input("¿Deseas continuar? (s/n): ").strip().lower()
    if confirm != "s":
        print("Operación cancelada.")
        sys.exit(0)

    tracker = DeployTracker()
    db_info = f"Conectado a '{db_name}' en {db_host}:{db_port} (usuario: {db_user})"

    # Migrate
    tracker.reset(STEP_MIGRATE)
    tracker.start(STEP_MIGRATE)
    tracker.success(STEP_MIGRATE, db_info)

    try:
        print("\nEjecutando migrate...")
        call_command("migrate")
        msg = "Migraciones aplicadas exitosamente."
        print(msg)
        tracker.success(STEP_MIGRATE, msg)
        tracker.complete(STEP_MIGRATE, status_info=msg)
    except Exception as e:
        msg = f"Error al ejecutar migrate: {e}"
        print(msg)
        tracker.error(STEP_MIGRATE, msg)
        tracker.fail(STEP_MIGRATE, status_info=msg)
        sys.exit(1)

    # Create superuser
    tracker.reset(STEP_SUPERUSER)
    tracker.start(STEP_SUPERUSER)
    tracker.success(STEP_SUPERUSER, db_info)

    try:
        print("\nCreando superusuario...")
        call_command("createsuperuser")
        msg = "Superusuario creado exitosamente."
        print(msg)
        tracker.success(STEP_SUPERUSER, msg)
        tracker.complete(STEP_SUPERUSER, status_info=msg)
    except KeyboardInterrupt:
        msg = "Creación de superusuario cancelada por el usuario."
        print(f"\n{msg}")
        tracker.warning(STEP_SUPERUSER, msg)
        tracker.complete(STEP_SUPERUSER, status_info=msg)
    except Exception as e:
        msg = f"Error al crear superusuario: {e}"
        print(msg)
        tracker.error(STEP_SUPERUSER, msg)
        tracker.fail(STEP_SUPERUSER, status_info=msg)


if __name__ == "__main__":
    main()
