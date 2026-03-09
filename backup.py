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
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ipsec_back.settings")

import django

django.setup()

from django.core.management import call_command

BASE_DIR = Path(__file__).resolve().parent
CONFIG_FILE = BASE_DIR / "backup_models.json"
BACKUP_DIR = BASE_DIR / "backups"


def main():
    if not CONFIG_FILE.is_file():
        print(f"ERROR: Config file not found: {CONFIG_FILE}")
        sys.exit(1)

    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        models = json.load(f)

    if not isinstance(models, list) or not models:
        print("ERROR: backup_models.json must contain a non-empty JSON array.")
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
            ok += 1
        except Exception as exc:
            print(f"  FAIL  {model_label}: {exc}")
            fail += 1

    print(f"\nDone: {ok} succeeded, {fail} failed.")
    print(f"Backups saved in: {output_dir}")


if __name__ == "__main__":
    main()
