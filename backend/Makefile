# Makefile — ArdhiTrust backend developer commands
.PHONY: help up down build migrate makemigrations shell test lint audit createsuperuser logs

SETTINGS ?= config.settings.development

help:
	@echo "ArdhiTrust Backend"
	@echo "------------------"
	@echo "  make up               Start all services (Docker)"
	@echo "  make down             Stop all services"
	@echo "  make build            Rebuild Docker images"
	@echo "  make migrate          Run migrations"
	@echo "  make makemigrations   Create new migrations"
	@echo "  make shell            Django shell"
	@echo "  make test             Run test suite"
	@echo "  make lint             Run ruff + mypy"
	@echo "  make audit            Run bandit + pip-audit"
	@echo "  make createsuperuser  Create admin user"
	@echo "  make logs             Follow all container logs"

up:
	docker compose up -d

down:
	docker compose down

build:
	docker compose build

migrate:
	DJANGO_SETTINGS_MODULE=$(SETTINGS) python manage.py migrate

makemigrations:
	DJANGO_SETTINGS_MODULE=$(SETTINGS) python manage.py makemigrations

shell:
	DJANGO_SETTINGS_MODULE=$(SETTINGS) python manage.py shell_plus

test:
	DJANGO_SETTINGS_MODULE=config.settings.test \
	pytest --cov=apps --cov-report=term-missing --cov-fail-under=80 -v

test-fast:
	DJANGO_SETTINGS_MODULE=config.settings.test \
	pytest --cov=apps -q -x

lint:
	ruff check .
	mypy apps/ config/

audit:
	bandit -r apps/ config/ -ll
	pip-audit

createsuperuser:
	DJANGO_SETTINGS_MODULE=$(SETTINGS) python manage.py createsuperuser

logs:
	docker compose logs -f

# Dev server (without Docker)
run:
	DJANGO_SETTINGS_MODULE=$(SETTINGS) python manage.py runserver 0.0.0.0:8000

# Celery worker (without Docker)
worker:
	DJANGO_SETTINGS_MODULE=$(SETTINGS) celery -A config worker -l info -Q default,verification,payments,ai_agents

# Collect static files
static:
	DJANGO_SETTINGS_MODULE=$(SETTINGS) python manage.py collectstatic --noinput