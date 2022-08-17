.PHONY: init build run db-migrate build-dependencies db-init db-migrate db-upgrade

init:  build run
	docker-compose exec app flask db init
	docker-compose exec app flask db upgrade
	docker-compose exec app flask init
	@echo "Init done, containers running"

build:
	docker-compose build

run:
	docker-compose up -d

build-dependencies:
	pip-compile -v -r requirements.in

db-init:
	docker-compose exec app flask db init

db-migrate:
	docker-compose exec app flask db migrate

db-upgrade:
	docker-compose exec app flask db upgrade
