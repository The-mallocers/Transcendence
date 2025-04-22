DOCKER_COMPOSE_FILE=docker-compose.yml

up:
	rm -rf ./docker/staticdocker
	docker compose -f ./$(DOCKER_COMPOSE_FILE) up -d --build --no-attach mailhog --no-attach alertmanager --no-attach grafana

down:
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

reload:
	cp -r static/css ./docker/staticdocker
	cp -r static/js ./docker/staticdocker