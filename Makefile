DOCKER_COMPOSE:=docker-compose --project-name=aiortc-media-proxy


build:
	$(DOCKER_COMPOSE) build

up:
	$(DOCKER_COMPOSE) up
