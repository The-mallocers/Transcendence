DOCKER_COMPOSE_FILE=docker-compose.yml
GENERATE_ENV_SCRIPT=./docker/generate_env.sh

# Color variables
RED=\033[0;31m
GREEN=\033[0;32m
YELLOW=\033[0;33m
BLUE=\033[0;34m
CYAN=\033[0;36m
NC=\033[0m

all: help

# =============================================================================
# Utility: .env check
# =============================================================================
check-env:
	@if [ ! -f .env ]; then \
		echo "$(RED).env file not found! Please run 'make env' to create it.$(NC)"; \
		exit 1; \
	fi

# =============================================================================
# 🛈 Help & Info
# =============================================================================

help:
	@echo ""
	@echo "$(CYAN)Usage:$(NC)"
	@echo "  make [target]"
	@echo ""
	@echo "$(CYAN)Description:$(NC)"
	@echo "  Transcendence Makefile provides various commands to manage the application lifecycle."
	@echo "  Use the following targets as needed."
	@echo ""
	@echo "$(CYAN)Available commands:$(NC)"
	@echo "  $(GREEN)make up$(NC)              - Start all containers (builds and attaches logs for django-web)"
	@echo "  $(GREEN)make detach$(NC)          - Start all containers in detached mode (no logs attached)"
	@echo "  $(GREEN)make down$(NC)            - Stop all running containers"
	@echo "  $(GREEN)make test$(NC)            - Run tests inside the Docker environment"
	@echo "  $(GREEN)make test-coverage$(NC)   - Run tests with coverage report inside Docker"
	@echo "  $(GREEN)make logs$(NC)            - Show logs from all running containers"
	@echo "  $(GREEN)make status$(NC)          - Display the status of containers, volumes, and images"
	@echo "  $(GREEN)make restart$(NC)         - Stop and restart all containers"
	@echo "  $(GREEN)make reload$(NC)          - Reload static files into the application"
	@echo "  $(GREEN)make dbclean$(NC)         - Remove database volumes and clean up"
	@echo "  $(GREEN)make clean$(NC)           - Remove all containers, images, and prune the system"
	@echo "  $(GREEN)make re$(NC)              - Alias for 'restart'"
	@echo "  $(GREEN)make redetach$(NC)        - Restart all containers in detached mode"
	@echo "  $(GREEN)make env$(NC)             - Create or update the .env file and validate dependencies"
	@echo "  $(GREEN)make secrets$(NC)         - Create 42_client and 42_secret files in the secrets folder"
	@echo "  $(GREEN)make passwords$(NC)       - Update application/service passwords in .env"
	@echo ""
	@echo "$(CYAN)Notes:$(NC)"
	@echo "  - Commands using Docker Compose require Docker to be installed and running."
	@echo "  - Ensure you have the necessary permissions to execute these commands."
	@echo "  - For detailed logs, use 'make logs'."

# =============================================================================
# 🏗️  Build & Run
# =============================================================================
# env check-env
up: 
	@echo "$(CYAN)Bringing up containers...$(NC)"
	@rm -rf ./docker/staticdocker/
	@docker compose -f ./$(DOCKER_COMPOSE_FILE) down
	@docker compose -f ./$(DOCKER_COMPOSE_FILE) up --build --attach django-web

detach: env check-env
	@echo "$(CYAN)Bringing up containers in detached mode...$(NC)"
	@rm -rf ./docker/staticdocker/
	@docker compose -f ./$(DOCKER_COMPOSE_FILE) down
	@docker compose -f ./$(DOCKER_COMPOSE_FILE) up -d --build --no-attach mailhog --no-attach alertmanager --no-attach grafana

down: check-env
	@echo "$(YELLOW)Stopping containers...$(NC)"
	@docker compose -f ./$(DOCKER_COMPOSE_FILE) down

restart: down up
re: down up
redetach: down detach

status: check-env
	@echo "$(CYAN)Containers:$(NC)"
	@docker compose -f ./$(DOCKER_COMPOSE_FILE) ps
	@echo "$(CYAN)Volumes:$(NC)"
	@docker volume ls
	@echo "$(CYAN)Images:$(NC)"
	@docker image ls

logs: check-env
	@echo "$(CYAN)Showing logs...$(NC)"
	@docker compose -f ./$(DOCKER_COMPOSE_FILE) logs

# =============================================================================
# 🧪 Test & Coverage
# =============================================================================

test: env check-env
	@echo "$(CYAN)Running tests...$(NC)"
	@docker compose -f ./$(DOCKER_COMPOSE_FILE) up -d db redis
	@docker compose -f ./$(DOCKER_COMPOSE_FILE) exec -T db sh -c 'until pg_isready -U ${DATABASE_USERNAME} -d ${DATABASE_NAME}; do sleep 1; done'
	@docker compose -f ./$(DOCKER_COMPOSE_FILE) run --rm django-web sh -c "python manage.py test"
	@docker compose -f ./$(DOCKER_COMPOSE_FILE) down

test-coverage: env check-env
	@echo "$(CYAN)Running tests with coverage...$(NC)"
	@docker compose -f ./$(DOCKER_COMPOSE_FILE) up -d db redis
	@docker compose -f ./$(DOCKER_COMPOSE_FILE) exec -T db sh -c 'until pg_isready -U ${DATABASE_USERNAME} -d ${DATABASE_NAME}; do sleep 1; done'
	@docker compose -f ./$(DOCKER_COMPOSE_FILE) run --rm django-web sh -c "pip install coverage && coverage run --source='.' manage.py test && coverage report && coverage html && coverage xml -o coverage.xml"
	CONTAINER_ID=$$(docker compose -f ./$(DOCKER_COMPOSE_FILE) run -d --rm django-web sleep 5) && \
	@docker cp $$CONTAINER_ID:/app/coverage.xml ./coverage.xml && \
	@docker stop $$CONTAINER_ID
	@sed -i '' 's|<source>/app</source>|<source>$(PWD)</source>|g' coverage.xml
	@docker compose -f ./$(DOCKER_COMPOSE_FILE) down

# =============================================================================
# 🧹 Clean & Maintenance
# =============================================================================

dbclean: down
	@echo "$(YELLOW)Removing database volumes and cleaning up...$(NC)"
	@rm -rfd ./media
	@docker compose down -v
	@if [ "$$(docker ps -q)" ]; then \
		docker volume rm $$(docker volume ls -q) --force;\
	fi

clean: dbclean
	@echo "$(RED)Stopping and removing all containers and images...$(NC)"
	@if [ "$$(docker ps -q)" ]; then \
		docker stop $$(docker ps -q);\
	fi
	@if [ "$$(docker images -q)" ]; then \
		docker rmi $$(docker images -q) --force;\
	fi
	$(MAKE) dbclean
	@docker system prune -a --volumes --force

reload: check-env
	@echo "$(CYAN)Reloading static files...$(NC)"
	@cp -r static/css ./docker/staticdocker
	@cp -r static/js ./docker/staticdocker
	@cp -r static/assets ./docker/staticdocker
	@echo "$(GREEN)Static files reloaded$(NC)"

# =============================================================================
# ⚙️  Environment & Secrets
# =============================================================================

env: secrets
	@echo "$(CYAN)Creating or updating .env file and validating dependencies...$(NC)"
	@$(GENERATE_ENV_SCRIPT)

secrets:
	@mkdir -m 700 -p ./secrets
	@if [ ! -f ./secrets/42_client ]; then \
		echo "$(CYAN)Enter the key for 42_client:$(NC)"; \
		read client_key; \
		client_key=$$(echo "$$client_key" | tr -d '\r' | xargs); \
		printf "%s" "$$client_key" > ./secrets/42_client; \
	fi
	@if [ ! -f ./secrets/42_secret ]; then \
		echo "$(CYAN)Enter the key for 42_secret:$(NC)"; \
		read secret_key; \
		secret_key=$$(echo "$$secret_key" | tr -d '\r' | xargs); \
		printf "%s" "$$secret_key" > ./secrets/42_secret; \
	fi

passwords: check-env
	@echo "$(CYAN)Updating ADMIN_PWD, DATABASE_PASSWORD and GRAFANA_PASSWORD in .env...$(NC)"
	@if [ ! -f .env ]; then \
		echo "$(RED).env does not exist. Run 'make env' first.$(NC)"; \
		exit 1; \
	fi; \
	for var in ADMIN_PWD DATABASE_PASSWORD GRAFANA_PASSWORD; do \
		case $$var in \
			ADMIN_PWD) default="123456789!"; prompt="Set ADMIN_PWD";; \
			DATABASE_PASSWORD) default="admin"; prompt="Set DATABASE_PASSWORD";; \
			GRAFANA_PASSWORD) default="admin"; prompt="Set GRAFANA_PASSWORD";; \
		esac; \
		if [ -t 0 ]; then \
			read -p "$$prompt (default: $$default): " val; \
			val=$${val:-$$default}; \
		else \
			val=$$default; \
		fi; \
		if grep -q "^$$var=" .env; then \
			if [ "$$(uname)" = "Darwin" ]; then \
				sed -i '' "s/^$$var=.*/$$var='$$val'/" .env; \
			else \
				sed -i "s/^$$var=.*/$$var='$$val'/" .env; \
			fi; \
			echo "$(GREEN)$$var updated.$(NC)"; \
		else \
			echo "$$var='$$val'" >> .env; \
			echo "$(GREEN)$$var added.$(NC)"; \
		fi; \
	done
	@echo "$(CYAN)Done updating passwords.$(NC)"

.PHONY: help up down test test-coverage logs status restart dbclean reload clean re redetach env secrets passwords