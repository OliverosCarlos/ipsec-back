"""
restore.py — Restore backup data by selecting a backup folder interactively.

Usage (from the project root):
    python restore.py
"""

import os
import sys
from pathlib import Path

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ipsec_back.settings")

import django

django.setup()

from django.core.management import call_command

BACKUP_DIR = Path(__file__).resolve().parent / "backups"


def main():
    if not BACKUP_DIR.is_dir():
        print(f"ERROR: Backup directory not found: {BACKUP_DIR}")
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
        print(f"No JSON files found in {selected.name}/")
        sys.exit(1)

    print(f"\nRestoring {len(json_files)} file(s) from {selected.name}/\n")

    ok, fail = 0, 0
    for json_file in json_files:
        try:
            call_command("loaddata", str(json_file))
            print(f"  OK    {json_file.name}")
            ok += 1
        except Exception as exc:
            print(f"  FAIL  {json_file.name}: {exc}")
            fail += 1

    print(f"\nDone: {ok} succeeded, {fail} failed.")


if __name__ == "__main__":
    main()
