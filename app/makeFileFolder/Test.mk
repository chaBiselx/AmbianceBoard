FILTER ?= 

#all test
test : 
	@# Help: lance l'ensemble des test unitaire et fonctionnel
	@-if [ -z "$(FILTER)" ]; then \
		python manage.py test; \
	else \
		python manage.py test $(FILTER); \
	fi

