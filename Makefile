default: build run;

build:
	docker compose build

run:
	docker compose up

exec:
	docker exec -it '${container}' sh

migrate:
	alembic upgrade head

downgrade:
	alembic downgrade -1

migration:
	alembic revision --autogenerate -m '${msg}'

format:
	ruff check --fix

check:
	ruff check src
	mypy -p src