FILTER ?= 


## —— Tests  ————————————————————————————————————————————————————————————————
test-all: test-backend test-frontend
	@# Help: lance l'ensemble des tests (backend et frontend)

test-backend-coverage:
	@# Help: lance les tests backend avec couverture
	$(CONTAINER_BACKEND) sh -c "coverage run --source='.' manage.py test && coverage report"

test-backend: test-backend-tu test-backend-ti
	@# Help: lance l'ensemble des tests backend (unitaires et d'intégration)

test-backend-tu:
	@# Help: lance l'ensemble des test unitaire et fonctionnel
	@-if [ -z "$(FILTER)" ]; then \
		$(CONTAINER_BACKEND) python manage.py test --tag=unitaire --noinput; \
	else \
		$(CONTAINER_BACKEND) python manage.py test --tag=unitaire $(FILTER) --noinput; \
	fi

test-backend-ti:
	@# Help: lance les tests d'intégration
	@-if [ -z "$(FILTER)" ]; then \
		$(CONTAINER_BACKEND) python manage.py test --tag=integration --noinput; \
	else \
		$(CONTAINER_BACKEND) python manage.py test --tag=integration $(FILTER) --noinput; \
	fi

test-frontend: test-frontend-tu test-frontend-ti
	@# Help: lance l'ensemble des tests frontend (unitaires et d'intégration)

test-frontend-tu:
	@# Help: lance les tests unitaires frontend
	@-if [ -z "$(FILTER)" ]; then \
		$(CONTAINER_FRONTEND) npm run test:tu; \
	else \
		$(CONTAINER_FRONTEND) npm run test:tu -- --testNamePattern="$(FILTER)"; \
	fi

test-frontend-ti:
	@# Help: lance les tests d'intégration frontend
	@-if [ -z "$(FILTER)" ]; then \
		$(CONTAINER_FRONTEND) npm run test:ti; \
	else \
		$(CONTAINER_FRONTEND) npm run test:ti -- --testNamePattern="$(FILTER)"; \
	fi