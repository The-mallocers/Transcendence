DOCKER_COMPOSE_FILE=docker-compose.yml

# Show help
help:
	@echo "Available commands:"
	@echo "  make up              - Start all containers"
	@echo "  make down            - Stop all containers"
	@echo "  make test            - Run tests in Docker"
	@echo "  make test-coverage   - Run tests with coverage report in Docker"
	@echo "  make logs            - Show container logs"
	@echo "  make status          - Show container status"
	@echo "  make restart         - Restart all containers"
	@echo "  make reload          - Reload staticfile"
	@echo "  make dbclean         - Remove database volumes"
	@echo "  make clean           - Remove all containers and images"
	@echo "  make re              - Alias for restart"

up:
	rm -rf ./docker/staticdocker
	docker compose -f ./$(DOCKER_COMPOSE_FILE) up --build --attach django-web

detach:
	rm -rf ./docker/staticdocker
	docker compose -f ./$(DOCKER_COMPOSE_FILE) up -d --build --no-attach mailhog --no-attach alertmanager --no-attach grafana

down:
	docker compose -f ./$(DOCKER_COMPOSE_FILE) down

test:
	docker compose -f ./$(DOCKER_COMPOSE_FILE) up -d db redis
	docker compose -f ./$(DOCKER_COMPOSE_FILE) exec -T db sh -c 'until pg_isready -U ${DATABASE_USERNAME} -d ${DATABASE_NAME}; do sleep 1; done'
	docker compose -f ./$(DOCKER_COMPOSE_FILE) run --rm django-web sh -c "python manage.py test"
	docker compose -f ./$(DOCKER_COMPOSE_FILE) down

test-coverage:
	docker compose -f ./$(DOCKER_COMPOSE_FILE) up -d db redis
	docker compose -f ./$(DOCKER_COMPOSE_FILE) exec -T db sh -c 'until pg_isready -U ${DATABASE_USERNAME} -d ${DATABASE_NAME}; do sleep 1; done'
	docker compose -f ./$(DOCKER_COMPOSE_FILE) run --rm django-web sh -c "pip install coverage && coverage run --source='.' manage.py test && coverage report && coverage html && coverage xml -o coverage.xml"
	CONTAINER_ID=$$(docker compose -f ./$(DOCKER_COMPOSE_FILE) run -d --rm django-web sleep 5) && \
	docker cp $$CONTAINER_ID:/app/coverage.xml ./coverage.xml && \
	docker stop $$CONTAINER_ID
	sed -i '' 's|<source>/app</source>|<source>$(PWD)</source>|g' coverage.xml
	docker compose -f ./$(DOCKER_COMPOSE_FILE) down

logs:
	docker compose -f ./$(DOCKER_COMPOSE_FILE) logs

status:
	docker compose -f ./$(DOCKER_COMPOSE_FILE) ps && docker volume ls && docker image ls

restart: down up

dbclean:
	docker compose -f ./$(DOCKER_COMPOSE_FILE) down -v

reload:
	cp -r static/css ./docker/staticdocker
	cp -r static/js ./docker/staticdocker

clean: dbclean
	docker compose -f ./$(DOCKER_COMPOSE_FILE) down --rmi all

re: down up

redetach: down detach

.PHONY: help up down test test-coverage logs status restart dbclean reload clean re
