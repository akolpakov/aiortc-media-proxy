DOCKER_COMPOSE:=docker-compose --project-name=aiortc-media-proxy


build:
	$(DOCKER_COMPOSE) build

up:
	$(DOCKER_COMPOSE) up

docker-push-latest:
	docker build -t akolpakov/aiortc-media-proxy:latest .
	docker push akolpakov/aiortc-media-proxy:latest
