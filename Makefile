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

.PHONY: migrate makemigrations createsuperuser shell dbshell showmigrations collectstatic loaddata

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

## Run an arbitrary manage.py command (usage: make manage CMD="check --deploy")
manage:
	$(RUN) python manage.py $(CMD)
