import os
import shutil
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

BASE_DIR = Path(__file__).resolve().parent
BACKUP_DIR = BASE_DIR / "backups_employees"
MEDIA_ROOT = Path(settings.MEDIA_ROOT)
PHOTO_SUBDIR = "employees/photos"

STEP_CODE = "restore_employees"


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

    if not BACKUP_DIR.is_dir():
        msg = f"Backup directory not found: {BACKUP_DIR}"
        print(f"ERROR: {msg}")
        tracker.error(STEP_CODE, msg)
        tracker.fail(STEP_CODE, status_info=msg)
        sys.exit(1)

    folders = sorted(
        [d for d in BACKUP_DIR.iterdir() if d.is_dir()],
        key=lambda d: d.name,
    )

    if not folders:
        msg = "No backup folders found."
        print(msg)
        tracker.error(STEP_CODE, msg)
        tracker.fail(STEP_CODE, status_info=msg)
        sys.exit(1)

    print("\nBackups disponibles:\n")
    for i, folder in enumerate(folders, 1):
        json_count = len(list(folder.glob("*.json")))
        has_photos = (folder / "photos").is_dir()
        photo_info = f" + fotos" if has_photos else ""
        print(f"  {i}) {folder.name}  ({json_count} archivos{photo_info})")

    print()
    choice = input("Selecciona un backup a restaurar (número): ").strip()

    try:
        index = int(choice) - 1
        if index < 0 or index >= len(folders):
            raise ValueError
    except ValueError:
        print("Selección inválida.")
        sys.exit(1)

    selected = folders[index]
    json_files = sorted(selected.glob("*.json"))

    if not json_files:
        msg = f"No JSON files found in {selected.name}/"
        print(msg)
        tracker.error(STEP_CODE, msg)
        tracker.fail(STEP_CODE, status_info=msg)
        sys.exit(1)

    print(f"\nRestaurando {len(json_files)} archivo(s) desde {selected.name}/\n")

    # Restore models
    ok, fail = 0, 0
    for json_file in json_files:
        try:
            call_command("loaddata", str(json_file))
            print(f"  OK    {json_file.name}")
            tracker.success(STEP_CODE, f"{json_file.name}")
            ok += 1
        except Exception as exc:
            print(f"  FAIL  {json_file.name}: {exc}")
            tracker.error(STEP_CODE, f"{json_file.name}: {exc}")
            fail += 1

    # Restore photos
    photos_src = selected / "photos"
    photos_dst = MEDIA_ROOT / PHOTO_SUBDIR

    if photos_src.is_dir():
        photos = [f for f in photos_src.iterdir() if f.is_file()]
        if photos:
            photos_dst.mkdir(parents=True, exist_ok=True)
            for photo in photos:
                shutil.copy2(photo, photos_dst / photo.name)
            msg = f"{len(photos)} foto(s) restauradas en {PHOTO_SUBDIR}/"
            print(f"  OK    {msg}")
            tracker.success(STEP_CODE, msg)
        else:
            msg = "No se encontraron fotos en el backup."
            print(f"  WARN  {msg}")
            tracker.warning(STEP_CODE, msg)
    else:
        msg = "El backup no contiene directorio de fotos."
        print(f"  WARN  {msg}")
        tracker.warning(STEP_CODE, msg)

    summary = f"{ok} modelo(s) restaurados, {fail} fallidos. Desde: {selected.name}"
    print(f"\nDone: {summary}")

    if fail > 0:
        tracker.fail(STEP_CODE, status_info=summary)
    else:
        tracker.complete(STEP_CODE, status_info=summary)


if __name__ == "__main__":
    main()
