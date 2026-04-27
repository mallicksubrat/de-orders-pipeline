export PYTHONPATH := src

test:
	pytest -q

lint:
	ruff check src tests

run:
	python -m my_project.cli run

show-config:
	python -m my_project.cli show-config

docker-up:
	docker compose up -d postgres mock-api

docker-run:
	docker compose run --rm pipeline

docker-down:
	docker compose down --remove-orphans
