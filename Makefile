DOCKER_COMPOSE_FILE=docker-compose.yaml

up:
	rm -rf ./docker/staticdocker
	docker compose -f ./$(DOCKER_COMPOSE_FILE) up  --build --no-attach mailhog --no-attach alertmanager --no-attach grafana

down:
	docker compose -f ./$(DOCKER_COMPOSE_FILE) down

logs:
	docker compose -f ./$(DOCKER_COMPOSE_FILE) logs

status:
	docker compose -f ./$(DOCKER_COMPOSE_FILE) ps && docker volume ls && docker image ls

restart:
	down up

dbclean: down
	docker volume prune -f

clean: dbclean
	docker system prune -fa

volume:
	docker volume rm transcendence_grafana-data &&\
	docker volume rm transcendence_postgres-data &&\
	docker volume rm transcendence_prometheus-data