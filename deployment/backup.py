"""
backup.py — Standalone script to backup Django models listed in backup_models.json.

Usage (from the project root):
    python backup.py

Requires:
    - A valid .env file with database credentials
    - Django and project dependencies installed (pip install -r requirements.txt)
"""

import json
import os
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
CONFIG_FILE = BASE_DIR / "backup_models.json"
BACKUP_DIR = BASE_DIR / "backups"

STEP_CODE = "backup"


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

    if not CONFIG_FILE.is_file():
        msg = f"Config file not found: {CONFIG_FILE}"
        print(f"ERROR: {msg}")
        tracker.error(STEP_CODE, msg)
        tracker.fail(STEP_CODE, status_info=msg)
        sys.exit(1)

    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        models = json.load(f)

    if not isinstance(models, list) or not models:
        msg = "backup_models.json must contain a non-empty JSON array."
        print(f"ERROR: {msg}")
        tracker.error(STEP_CODE, msg)
        tracker.fail(STEP_CODE, status_info=msg)
        sys.exit(1)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = BACKUP_DIR / timestamp
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Backing up {len(models)} model(s) to {output_dir}/\n")

    ok, fail = 0, 0
    for model_label in models:
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

    summary = f"{ok} succeeded, {fail} failed. Backups saved in: {output_dir}"
    print(f"\nDone: {summary}")

    if fail > 0:
        tracker.fail(STEP_CODE, status_info=summary)
    else:
        tracker.complete(STEP_CODE, status_info=summary)


if __name__ == "__main__":
    main()
