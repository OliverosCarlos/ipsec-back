import json
import os
from datetime import datetime
from pathlib import Path

from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Backup database tables listed in a JSON config file using dumpdata."

    def add_arguments(self, parser):
        parser.add_argument(
            "--config",
            default="backup_models.json",
            help="Path to JSON file with model names (default: backup_models.json)",
        )
        parser.add_argument(
            "--output-dir",
            default="backups",
            help="Directory to save backup files (default: backups/)",
        )

    def handle(self, *args, **options):
        config_path = options["config"]
        output_dir = options["output_dir"]

        if not os.path.isfile(config_path):
            self.stderr.write(self.style.ERROR(f"Config file not found: {config_path}"))
            return

        with open(config_path, "r", encoding="utf-8") as f:
            models = json.load(f)

        if not isinstance(models, list) or not models:
            self.stderr.write(self.style.ERROR("Config file must contain a non-empty JSON array of model names."))
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = Path(output_dir) / timestamp
        backup_dir.mkdir(parents=True, exist_ok=True)

        self.stdout.write(self.style.MIGRATE_HEADING(f"Backing up {len(models)} model(s) to {backup_dir}/"))

        for model_label in models:
            filename = model_label.replace(".", "_") + ".json"
            filepath = backup_dir / filename

            try:
                with open(filepath, "w", encoding="utf-8") as out:
                    call_command("dumpdata", model_label, indent=2, stdout=out)
                self.stdout.write(self.style.SUCCESS(f"  OK  {model_label} -> {filepath}"))
            except Exception as exc:
                self.stderr.write(self.style.ERROR(f"  FAIL  {model_label}: {exc}"))

        self.stdout.write(self.style.SUCCESS(f"\nBackup complete: {backup_dir}"))
