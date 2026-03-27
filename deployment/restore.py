"""
restore.py — Restore backup data by selecting a backup folder interactively.

Usage (from the project root):
    python restore.py
"""

import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ipsec_back.settings")

import django

django.setup()

from django.core.management import call_command
from django.conf import settings

from deploy_tracker import DeployTracker

BACKUP_DIR = Path(__file__).resolve().parent / "backups"

STEP_CODE = "restore"


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
        print("No backup folders found.")
        sys.exit(1)

    print("Available backups:\n")
    for i, folder in enumerate(folders, 1):
        json_count = len(list(folder.glob("*.json")))
        print(f"  {i}) {folder.name}  ({json_count} files)")

    print()
    choice = input("Select a backup to restore (number): ").strip()

    try:
        index = int(choice) - 1
        if index < 0 or index >= len(folders):
            raise ValueError
    except ValueError:
        print("Invalid selection.")
        sys.exit(1)

    selected = folders[index]
    json_files = sorted(selected.glob("*.json"))

    if not json_files:
        msg = f"No JSON files found in {selected.name}/"
        print(msg)
        tracker.error(STEP_CODE, msg)
        tracker.fail(STEP_CODE, status_info=msg)
        sys.exit(1)

    print(f"\nRestoring {len(json_files)} file(s) from {selected.name}/\n")

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

    summary = f"{ok} succeeded, {fail} failed. Restored from: {selected.name}"
    print(f"\nDone: {summary}")

    if fail > 0:
        tracker.fail(STEP_CODE, status_info=summary)
    else:
        tracker.complete(STEP_CODE, status_info=summary)


if __name__ == "__main__":
    main()
