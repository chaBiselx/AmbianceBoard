FILTER ?= 


## —— Tests  ————————————————————————————————————————————————————————————————
test-all: test-backend test-frontend test-music-labeler
	@# Help: lance l'ensemble des tests (backend et frontend)

test-backend-coverage:
	@# Help: lance les tests backend avec couverture
	$(CONTAINER_BACKEND) sh -c "coverage run --source='.' manage.py test && coverage report"

test-backend: test-backend-tu test-backend-ti test-backend-st
	@# Help: lance l'ensemble des tests backend (unitaires et d'intégration)

test-backend-tu:
	@# Help: lance l'ensemble des test unitaire et fonctionnel
	@if [ -z "$(FILTER)" ]; then \
		$(CONTAINER_BACKEND) python manage.py test --tag=unitaire --noinput; \
	else \
		$(CONTAINER_BACKEND) python manage.py test --tag=unitaire $(FILTER) --noinput; \
	fi

test-backend-ti:
	@# Help: lance les tests d'intégration
	@if [ -z "$(FILTER)" ]; then \
		$(CONTAINER_BACKEND) python manage.py test --tag=integration --noinput; \
	else \
		$(CONTAINER_BACKEND) python manage.py test --tag=integration $(FILTER) --noinput; \
	fi

test-backend-st:
	@# Help: lance les tests de stress backend
	@if [ -z "$(FILTER)" ]; then \
		$(CONTAINER_BACKEND) python manage.py test --tag=stress-test --noinput; \
	else \
		$(CONTAINER_BACKEND) python manage.py test --tag=stress-test $(FILTER) --noinput; \
	fi

test-frontend: test-frontend-tu test-frontend-ti
	@# Help: lance l'ensemble des tests frontend (unitaires et d'intégration)

test-frontend-tu:
	@# Help: lance les tests unitaires frontend
	@if [ -z "$(FILTER)" ]; then \
		$(CONTAINER_FRONTEND) npm run test:tu; \
	else \
		$(CONTAINER_FRONTEND) npm run test:tu -- --testNamePattern="$(FILTER)"; \
	fi

test-frontend-ti:
	@# Help: lance les tests d'intégration frontend
	@if [ -z "$(FILTER)" ]; then \
		$(CONTAINER_FRONTEND) npm run test:ti; \
	else \
		$(CONTAINER_FRONTEND) npm run test:ti -- --testNamePattern="$(FILTER)"; \
	fi

test-music-labeler: test-music-labeler-tu
	@# Help: lance l'ensemble des tests music labeler (unitaires et d'intégration)

test-music-labeler-tu:
	@# Help: lance les tests unitaires music labeler
	@if [ -z "$(FILTER)" ]; then \
		$(CONTAINER_MUSIC_LABELER) python -m pytest -q tests; \
	else \
		$(CONTAINER_MUSIC_LABELER) python -m pytest -q $(FILTER); \
	fi

test-e2e:
	@# Help: lance les tests E2E Playwright avec SQLite en surchargeant les variables de base de données
	@echo "$(GREEN)Migration et chargement des fixtures sur back avec SQLite...$(NC)"
	docker compose --profile test run --rm \
		-e SQL_ENGINE=django.db.backends.sqlite3 \
		-e SQL_DATABASE=/usr/src/db.sqlite3 \
		-e SQL_USER= \
		-e SQL_PASSWORD= \
		-e SQL_HOST=localhost \
		-e SQL_PORT=5432 \
		back sh -c "\
			python manage.py migrate && \
			python manage.py create_root_user && \
			python manage.py seed_dev && \
			python manage.py seed_public_soundboard && \
			python manage.py seed_playlist_tags && \
			python manage.py seed_soundboard_tags && \
			python manage.py seed_E2E_public_soundboard"
	@echo "$(GREEN)Démarrage de back avec SQLite...$(NC)"
	docker compose --profile test up -d back
	@until $(CONTAINER_BACKEND) python manage.py check --database default > /dev/null 2>&1; do sleep 2; done
	docker compose --profile test run --rm playwright

test-stress: test-backend-st
	@# Help: lance les tests de stress