# ──────────────────────────────────────────────
# Makefile for ipsec-back one-shot Django tasks
# ──────────────────────────────────────────────

DOCKER_REGISTRY ?= localhost:5000
IMAGE_TAG       ?= latest
IMAGE_NAME       = $(DOCKER_REGISTRY)/ipsec-back:$(IMAGE_TAG)
NETWORK          = core_gateway_network

# Common docker run flags for one-shot jobs
RUN = docker run --rm \
	--env-file .env \
	--network $(NETWORK) \
	$(IMAGE_NAME)

.PHONY: migrate makemigrations createsuperuser shell dbshell showmigrations collectstatic loaddata restoredata backupdata

## Run pending migrations
migrate:
	$(RUN) python manage.py migrate --noinput

## Create new migration files
makemigrations:
	$(RUN) python manage.py makemigrations

## Show migration status
showmigrations:
	$(RUN) python manage.py showmigrations

## Collect static files
collectstatic:
	$(RUN) python manage.py collectstatic --noinput

## Create a superuser interactively
createsuperuser:
	docker run --rm -it \
		--env-file .env \
		--network $(NETWORK) \
		$(IMAGE_NAME) python manage.py createsuperuser

## Open a Django shell
shell:
	docker run --rm -it \
		--env-file .env \
		--network $(NETWORK) \
		$(IMAGE_NAME) python manage.py shell

## Open a database shell
dbshell:
	docker run --rm -it \
		--env-file .env \
		--network $(NETWORK) \
		$(IMAGE_NAME) python manage.py dbshell

## Load fixture data (usage: make loaddata FIXTURE=countries)
loaddata:
	$(RUN) python manage.py loaddata $(FIXTURE)

## Restore a backup interactively (usage: make restoredata)
restoredata:
	docker run --rm -it \
		--env-file .env \
		--network $(NETWORK) \
		-v $$(pwd)/backups:/app/backups \
		-v $$(pwd)/restore.py:/app/restore.py:ro \
		$(IMAGE_NAME) python restore.py

## Backup database tables to JSON (usage: make backupdata)
backupdata:
	docker run --rm \
		--env-file .env \
		--network $(NETWORK) \
		-v $$(pwd)/backups:/app/backups \
		-v $$(pwd)/backup_models.json:/app/backup_models.json:ro \
		$(IMAGE_NAME) python manage.py backupdata

## Run an arbitrary manage.py command (usage: make manage CMD="check --deploy")
manage:
	$(RUN) python manage.py $(CMD)
