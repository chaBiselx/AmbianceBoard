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
	@make -pqR : 2>/dev/null \
        | awk -v RS= -F: '/^# File/,/^# Finished Make data base/ {if ($$1 !~ "^[#.]") {print $$1}}' \
        | sort \
        | egrep -v -e '^[^[:alnum:]]' -e '^$@$$' \
        | xargs -I _ sh -c 'printf "%-20s " _; make _ -nB | (grep -i "^# Help:" || echo "") | tail -1 | sed "s/^# Help: //g"'


include makeFileFolder/Backend.mk
include makeFileFolder/Test.mk
