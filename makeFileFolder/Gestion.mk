build:
	@# Help: Construire les ressources de l'application
	@if [ ! -f ".env" ]; then \
		@cp .env.dev.sample .env; \
	fi
	@docker compose build --no-cache

up:
	@# Help: Demarrer les ressources de l'application
	@docker compose up

down:
	@# Help: Arrêter les ressources de l'application
	@docker compose down

resource: 
	@# Help: Consulter les ressources de l'application
	@./makeFileFolder/sh/docker_resources.sh

enter:
	@# Help: Entrer dans un conteneur Docker (usage: make enter S [I=1])
	@if [ -z "$(S)" ]; then \
		echo "Erreur: Vous devez spécifier un service. Usage: make enter S=nom_du_service [I=1]"; \
		exit 1; \
	fi
	@I=$${I:-1}; \
	CONTAINER_NAME="ambianceboard-$(S)-$$I"; \
	echo "Connexion au conteneur $$CONTAINER_NAME..."; \
	docker exec -it $$CONTAINER_NAME bash

