import os
import shutil
import sys
from datetime import datetime
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

BASE_DIR = Path(__file__).resolve().parent
BACKUP_DIR = BASE_DIR / "backups_employees"
MEDIA_ROOT = Path(settings.MEDIA_ROOT)
PHOTO_SUBDIR = "employees/photos"

MODELS = ["core.Account", "entities.Employee"]
STEP_CODE = "backup_employees"


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
    tracker.reset(STEP_CODE)
    tracker.start(STEP_CODE)
    tracker.success(STEP_CODE, f"Conectado a '{db_name}' en {db_host}:{db_port} (usuario: {db_user})")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = BACKUP_DIR / timestamp
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\nBackup de empleados y cuentas en {output_dir}/\n")

    # Backup models
    ok, fail = 0, 0
    for model_label in MODELS:
        filename = model_label.replace(".", "_") + ".json"
        filepath = output_dir / filename

        try:
            with open(filepath, "w", encoding="utf-8") as out:
                call_command("dumpdata", model_label, indent=2, stdout=out)
            print(f"  OK    {model_label} -> {filepath.name}")
            tracker.success(STEP_CODE, f"{model_label} -> {filepath.name}")
            ok += 1
        except Exception as exc:
            print(f"  FAIL  {model_label}: {exc}")
            tracker.error(STEP_CODE, f"{model_label}: {exc}")
            fail += 1

    # Backup photos
    photos_src = MEDIA_ROOT / PHOTO_SUBDIR
    photos_dst = output_dir / "photos"

    if photos_src.is_dir():
        files = [f for f in photos_src.iterdir() if f.is_file()]
        if files:
            photos_dst.mkdir(parents=True, exist_ok=True)
            for photo in files:
                shutil.copy2(photo, photos_dst / photo.name)
            msg = f"{len(files)} foto(s) copiadas a {photos_dst.name}/"
            print(f"  OK    {msg}")
            tracker.success(STEP_CODE, msg)
        else:
            msg = "No se encontraron fotos de empleados."
            print(f"  WARN  {msg}")
            tracker.warning(STEP_CODE, msg)
    else:
        msg = f"Directorio de fotos no encontrado: {photos_src}"
        print(f"  WARN  {msg}")
        tracker.warning(STEP_CODE, msg)

    summary = f"{ok} modelo(s) exportados, {fail} fallidos. Backup en: {output_dir.name}"
    print(f"\nDone: {summary}")

    if fail > 0:
        tracker.fail(STEP_CODE, status_info=summary)
    else:
        tracker.complete(STEP_CODE, status_info=summary)


if __name__ == "__main__":
    main()
