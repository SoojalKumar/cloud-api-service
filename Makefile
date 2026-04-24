.PHONY: run test migrate seed-demo reset-db show-config docker-build docker-run

run:
	uvicorn app.main:app --reload

test:
	python -m pytest

migrate:
	python -m app.cli migrate

seed-demo:
	python -m app.cli seed-demo

reset-db:
	python -m app.cli reset-db --yes

show-config:
	python -m app.cli show-config

docker-build:
	docker build -t cloud-api-service .

docker-run:
	docker run -p 8000:8000 cloud-api-service
