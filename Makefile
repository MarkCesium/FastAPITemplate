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
	uv run ruff check --fix .
	uv run ruff format .

check:
	uv run ruff check src
	uv run mypy src