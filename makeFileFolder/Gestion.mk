init:
	@# Help: Initialiser les ressources de l'application
	@if [ ! -f ".env" ]; then \
		@cp .env.dev.sample .env; \
	fi

init-prod:
	@# Help: Initialiser les ressources de l'application en mode production
	@if [ ! -f ".env" ]; then \
		@cp .env.prod.sample .env; \
	fi
	@if [ ! -f "nginx/cert.pem" ] || [ ! -f "nginx/key.pem" ]; then \
		echo "[ERREUR] Certificat SSL manquant : nginx/cert.pem ou nginx/key.pem"; \
		echo "Générez un certificat SSL avant de lancer la production (voir documentation)"; \
		exit 1; \
	else \
		echo "[OK] Certificats SSL trouvés."; \
	fi

build:
	@# Help: Construire les ressources de l'application
	@docker compose build --no-cache

build-prod:
	@# Help: Construire les ressources de l'application en mode production
	@docker compose -f docker-compose.prod.yml build --no-cache

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

