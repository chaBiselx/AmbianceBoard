## —— Gestion  ————————————————————————————————————————————————————————————————
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

## —— Docker  ————————————————————————————————————————————————————————————————
restart: down up
	@# Help: Redémarrer les ressources de l'application

build:
	@# Help: Construire les ressources de l'application
	@FRONT_UID=$$(id -u) FRONT_GID=$$(id -g) docker compose build --no-cache

build-prod:
	@# Help: Construire les ressources de l'application en mode production
	@cd app && ./build-prod.sh

up: clear-old-containers
	@# Help: Demarrer les ressources de l'application
	@FRONT_UID=$$(id -u) FRONT_GID=$$(id -g) docker compose up -d
	@FRONT_UID=$$(id -u) FRONT_GID=$$(id -g) docker compose logs -f back front db cronjob

clear-old-containers:
	@# Help: Supprimer les anciens conteneurs Docker
	@docker container prune -f
	@docker volume prune -f
	@docker image prune -f

down:
	@# Help: Arrêter les ressources de l'application
	@docker compose down

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

images-size:
	@# Help: Afficher le poids des images Docker du projet (trié par nom)
	@echo "Poids des images Docker du projet :"
	@docker compose config --images | xargs -I{} docker image inspect {} --format '{{.RepoTags}} {{.Id}}' 2>/dev/null | \
		awk '{id=$$NF; tags=$$0; sub(/ [^ ]+$$/, "", tags); print tags, id}' | \
		while read tags id; do \
			docker image ls --no-trunc --format "{{.Repository}}:{{.Tag}}\t{{.Size}}\t{{.ID}}" | \
			grep "$$id" | awk -v t="$$tags" '{printf "%-50s %s\n", t, $$2}'; \
		done | sort
	@echo "---"
	@echo "Total des images :"
	@docker compose config --images | xargs docker image inspect --format '{{.Size}}' 2>/dev/null | \
		awk '{sum+=$$1} END {printf "%.2f MB\n", sum/1024/1024}'

## —— DEBUG  ————————————————————————————————————————————————————————————————
debug-fix-front-perms:
	@# Help: Réparer les permissions du frontend (node_modules) pour l'utilisateur node
	@echo "Réparation des permissions frontend..."
	@docker compose exec -u root front sh -lc 'chown -R node:node /app 2>/dev/null || true'
	@docker compose exec front sh -lc 'id && ls -ld /app /app/node_modules 2>/dev/null || true'

