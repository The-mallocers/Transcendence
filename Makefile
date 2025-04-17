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
	@echo "  make dbclean         - Remove database volumes"
	@echo "  make clean           - Remove all containers and images"
	@echo "  make re              - Alias for restart"

up:
	rm -rf ./docker/staticdocker
	docker compose -f ./$(DOCKER_COMPOSE_FILE) up  --build --no-attach mailhog --no-attach alertmanager --no-attach grafana

down:
	docker compose -f ./$(DOCKER_COMPOSE_FILE) down

test:
	# Start only the necessary services for testing (database and redis)
	docker compose -f ./$(DOCKER_COMPOSE_FILE) up -d db redis
	# Wait for services to be ready
	docker compose -f ./$(DOCKER_COMPOSE_FILE) exec -T db sh -c 'until pg_isready -U ${DATABASE_USERNAME} -d ${DATABASE_NAME}; do sleep 1; done'
	# Run tests in the Django container
	docker compose -f ./$(DOCKER_COMPOSE_FILE) run --rm django-web sh -c "python manage.py test"
	# Clean up after tests
	docker compose -f ./$(DOCKER_COMPOSE_FILE) down

test-coverage:
	# Start only the necessary services for testing (database and redis)
	docker compose -f ./$(DOCKER_COMPOSE_FILE) up -d db redis
	# Wait for services to be ready
	docker compose -f ./$(DOCKER_COMPOSE_FILE) exec -T db sh -c 'until pg_isready -U ${DATABASE_USERNAME} -d ${DATABASE_NAME}; do sleep 1; done'
	# Run tests with coverage in the Django container
	docker compose -f ./$(DOCKER_COMPOSE_FILE) run --rm django-web sh -c "pip install coverage && coverage run --source='.' manage.py test && coverage report && coverage html"
	# Clean up after tests
	docker compose -f ./$(DOCKER_COMPOSE_FILE) down


logs:
	docker compose -f ./$(DOCKER_COMPOSE_FILE) logs

status:
	docker compose -f ./$(DOCKER_COMPOSE_FILE) ps && docker volume ls && docker image ls

restart: down up

dbclean:
	docker compose down -v

clean: dbclean
	docker compose down --rmi all

re: down up
