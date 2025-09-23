FILTER ?= 

test-all: test-backend-tu test-frontend-tu
	@# Help: lance l'ensemble des tests (backend et frontend)

#all test
test-backend-tu:
	@# Help: lance l'ensemble des test unitaire et fonctionnel
	@-if [ -z "$(FILTER)" ]; then \
		$(CONTAINER_BACKEND) python manage.py test --noinput; \
	else \
		$(CONTAINER_BACKEND) python manage.py test $(FILTER) --noinput; \
	fi

test-frontend-tu:
	@# Help: lance les tests frontend
	@-if [ -z "$(FILTER)" ]; then \
		$(CONTAINER_FRONTEND) npm run test; \
	else \
		$(CONTAINER_FRONTEND) npm run test:$(FILTER); \
	fi