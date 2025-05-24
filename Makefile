DOCKER_COMPOSE_FILE=docker-compose.yml
GENERATE_ENV_SCRIPT=./docker/generate_env.sh

# Show help
help:
	@echo "\n${CYAN}Usage:${NC}"
	@echo "  make [target]"
	@echo "\n${CYAN}Description:${NC}"
	@echo "  Transcendence Makefile provides various commands to manage the application lifecycle."
	@echo "  Use the following targets as needed."
	@echo "\n${CYAN}Available commands:${NC}"
	@echo "  ${GREEN}make up${NC}              - Start all containers (builds and attaches logs for django-web)"
	@echo "  ${GREEN}make detach${NC}          - Start all containers in detached mode (no logs attached)"
	@echo "  ${GREEN}make down${NC}            - Stop all running containers"
	@echo "  ${GREEN}make test${NC}            - Run tests inside the Docker environment"
	@echo "  ${GREEN}make test-coverage${NC}   - Run tests with coverage report inside Docker"
	@echo "  ${GREEN}make logs${NC}            - Show logs from all running containers"
	@echo "  ${GREEN}make status${NC}          - Display the status of containers, volumes, and images"
	@echo "  ${GREEN}make restart${NC}         - Stop and restart all containers"
	@echo "  ${GREEN}make reload${NC}          - Reload static files into the application"
	@echo "  ${GREEN}make dbclean${NC}         - Remove database volumes and clean up"
	@echo "  ${GREEN}make clean${NC}           - Remove all containers, images, and prune the system"
	@echo "  ${GREEN}make re${NC}              - Alias for 'restart'"
	@echo "  ${GREEN}make redetach${NC}        - Restart all containers in detached mode"
	@echo "  ${GREEN}make env${NC}             - Create or update the .env file and validate dependencies"
	@echo "  ${GREEN}make secrets${NC}         - Create 42_client and 42_secret files in the secrets folder"
	@echo "\n${CYAN}Notes:${NC}"
	@echo "  - Commands using Docker Compose require Docker to be installed and running."
	@echo "  - Ensure you have the necessary permissions to execute these commands."
	@echo "  - For detailed logs, use 'make logs'."

up: env
	@rm -rf ./docker/staticdocker/
	@docker compose -f ./$(DOCKER_COMPOSE_FILE) down
	@docker compose -f ./$(DOCKER_COMPOSE_FILE) up --build --attach django-web

detach: env
	@rm -rf ./docker/staticdocker/
	@docker compose -f ./$(DOCKER_COMPOSE_FILE) down
	@docker compose -f ./$(DOCKER_COMPOSE_FILE) up -d --build --no-attach mailhog --no-attach alertmanager --no-attach grafana

down:
	@docker compose -f ./$(DOCKER_COMPOSE_FILE) down

test: env
	@docker compose -f ./$(DOCKER_COMPOSE_FILE) up -d db redis
	@docker compose -f ./$(DOCKER_COMPOSE_FILE) exec -T db sh -c 'until pg_isready -U ${DATABASE_USERNAME} -d ${DATABASE_NAME}; do sleep 1; done'
	@docker compose -f ./$(DOCKER_COMPOSE_FILE) run --rm django-web sh -c "python manage.py test"
	@docker compose -f ./$(DOCKER_COMPOSE_FILE) down

test-coverage: env
	@docker compose -f ./$(DOCKER_COMPOSE_FILE) up -d db redis
	@docker compose -f ./$(DOCKER_COMPOSE_FILE) exec -T db sh -c 'until pg_isready -U ${DATABASE_USERNAME} -d ${DATABASE_NAME}; do sleep 1; done'
	@docker compose -f ./$(DOCKER_COMPOSE_FILE) run --rm django-web sh -c "pip install coverage && coverage run --source='.' manage.py test && coverage report && coverage html && coverage xml -o coverage.xml"
	CONTAINER_ID=$$(docker compose -f ./$(DOCKER_COMPOSE_FILE) run -d --rm django-web sleep 5) && \
	@docker cp $$CONTAINER_ID:/app/coverage.xml ./coverage.xml && \
	@docker stop $$CONTAINER_ID
	@sed -i '' 's|<source>/app</source>|<source>$(PWD)</source>|g' coverage.xml
	@docker compose -f ./$(DOCKER_COMPOSE_FILE) down

logs:
	@docker compose -f ./$(DOCKER_COMPOSE_FILE) logs

status:
	@docker compose -f ./$(DOCKER_COMPOSE_FILE) ps && docker volume ls && docker image ls

restart: down up

dbclean: down
	@docker compose down -v
	@if [ "$$(docker ps -q)" ]; then \
		docker volume rm $$(docker volume ls -q) --force;\
	fi

reload:
	@cp -r static/css ./docker/staticdocker
	@cp -r static/js ./docker/staticdocker
	@cp -r static/assets ./docker/staticdocker
	@echo "Static files reloaded"

clean:
	@if [ "$$(docker ps -q)" ]; then \
		docker stop $$(docker ps -q);\
	fi
	@if [ "$$(docker images -q)" ]; then \
		docker rmi $$(docker images -q) --force;\
	fi
	$(MAKE) dbclean
	@docker system prune -a --volumes --force

re: down up

redetach: down detach

# Create or update .env file and validate dependencies
env:
	@$(GENERATE_ENV_SCRIPT)

# Create 42_client and 42_secret files
secrets:
	@mkdir -p ./secrets
	@if [ ! -f ./secrets/42_client ]; then \
		echo "Enter the key for 42_client:"; \
		read client_key; \
		echo "$$client_key" > ./secrets/42_client; \
		echo "42_client file created."; \
	else \
		echo "42_client file already exists."; \
	fi
	@if [ ! -f ./secrets/42_secret ]; then \
		echo "Enter the key for 42_secret:"; \
		read secret_key; \
		echo "$$secret_key" > ./secrets/42_secret; \
		echo "42_secret file created."; \
	else \
		echo "42_secret file already exists."; \
	fi

.PHONY: help up down test test-coverage logs status restart dbclean reload clean re env secrets