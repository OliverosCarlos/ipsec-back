"""
backup_model.py — Standalone script to backup a single Django model.

Usage (from the project root):
    python deployment/backup_model.py <app_label.ModelName>

Example:
    python deployment/backup_model.py entities.Bank

Requires:
    - A valid .env file with database credentials
    - Django and project dependencies installed (pip install -r requirements.txt)
"""

import argparse
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
BACKUP_DIR = BASE_DIR / "backups"

STEP_CODE = "backup_model"


def main():
    parser = argparse.ArgumentParser(
        description="Backup a single Django model to a JSON fixture."
    )
    parser.add_argument(
        "model",
        help="Model label in the form '<app_label>.<ModelName>' (e.g. 'entities.Bank').",
    )
    args = parser.parse_args()
    model_label = args.model

    db_conf = settings.DATABASES["default"]
    db_name = db_conf["NAME"]
    db_host = db_conf["HOST"]
    db_port = db_conf["PORT"]
    db_user = db_conf["USER"]

    print(f"\nBase de datos: '{db_name}' en {db_host}:{db_port} con usuario '{db_user}'")
    print(f"Modelo a respaldar: {model_label}")
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

    filename = model_label.replace(".", "_") + ".json"
    filepath = output_dir / filename

    print(f"Backing up {model_label} to {filepath}\n")

    try:
        with open(filepath, "w", encoding="utf-8") as out:
            call_command("dumpdata", model_label, indent=2, stdout=out)
        summary = f"{model_label} -> {filepath}"
        print(f"  OK    {summary}")
        tracker.success(STEP_CODE, summary)
        tracker.complete(STEP_CODE, status_info=summary)
    except Exception as exc:
        msg = f"{model_label}: {exc}"
        print(f"  FAIL  {msg}")
        tracker.error(STEP_CODE, msg)
        tracker.fail(STEP_CODE, status_info=msg)
        sys.exit(1)


if __name__ == "__main__":
    main()
