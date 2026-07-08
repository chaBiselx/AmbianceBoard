# flags 
MAKEFLAGS += --no-print-directory

# Couleurs for echo
GREEN = \033[0;32m
YELLOW = \033[0;33m
RED = \033[0;31m
GREY = \033[0;37m
NC = \033[0m  # No Color (reinit)

# CONST
CONTAINER_BACKEND=docker compose exec back
CONTAINER_CRONJOB=docker compose exec cronjob
CONTAINER_FRONTEND=docker compose exec -w /app front


help:
	@printf "%-20s %s\n" "Target" "Description"
	@printf "%-20s %s\n" "------" "-----------"
	@awk 'BEGIN{target=""} \
		/^## ——/{print ""; print $$0; next} \
		/^[a-z][a-z0-9-]*:/{target=$$1; gsub(/:/, "", target)} \
		/^[[:space:]]*@# Help:/{gsub(/^[[:space:]]*@# Help: /, "", $$0); printf "%-20s %s\n", target, $$0}' \
		makeFileFolder/*.mk


include makeFileFolder/Backend.mk
include makeFileFolder/Test.mk
include makeFileFolder/Gestion.mk
