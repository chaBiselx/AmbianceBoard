# Variables
BACKUP_DIR=./backup
MEDIA_FOLDER=./mediafiles
MEDIA_BACKUP=$(BACKUP_DIR)/media_backup.tar.gz
DATA_BACKUP=$(BACKUP_DIR)/data.json
LOG_DIR=./logs

## —— Dumbs/Load BDD  ————————————————————————————————————————————————————————————————
# Dump des données et des fichiers médias
dump: 
	@# Help: Exporte la base de données et les fichiers médias afin de pouvoir les restaurer plus tard
	$(MAKE) .prepare
	@echo "$(GREEN)Sauvegarde de la base de données...$(NC)"
	$(CONTAINER_BACKEND) ls ${BACKUP_DIR}
	$(CONTAINER_BACKEND) sh -c "python manage.py dumpdata --exclude contenttypes --exclude auth.permission > $(DATA_BACKUP)"
	@echo "$(GREEN)Sauvegarde des fichiers médias...$(NC)"
	$(CONTAINER_BACKEND) tar -czf $(MEDIA_BACKUP) $(MEDIA_FOLDER)/
	@echo "$(GREEN)Dump terminé : $(DATA_BACKUP) et $(MEDIA_BACKUP)$(NC)"
 
# Chargement des données et des fichiers médias
load: 
	@# Help: Restaure la base de données et les fichiers médias
	$(MAKE) .prepare
	@echo "$(GREEN)Migrate de la base de données...$(NC)"
	$(CONTAINER_BACKEND) python manage.py migrate 
	@echo "$(GREEN)Restauration des fichiers médias...$(NC)"
	$(CONTAINER_BACKEND) tar -xzf $(MEDIA_BACKUP)
	@echo "$(GREEN)Restauration de la base de données...$(NC)"
	$(CONTAINER_BACKEND) python manage.py loaddata $(DATA_BACKUP)
	@echo "$(GREEN)Restauration terminée.$(NC)"

#nettoyage des fichier de logs
clean:
	@# Help: vide les fichiers de logs sans les supprimer
	$(CONTAINER_BACKEND) find $(LOG_DIR) -type f -name "*.log" -exec sh -c '>'{}'; echo "Logs vidés pour {}"' \;

delete-db:
	@# Help: purge la base de données et supprime les fichiers médias
	@echo "$(GREEN)Suppression des fichiers médias...$(NC)"
	$(CONTAINER_BACKEND) rm -rf $(MEDIA_FOLDER)/*
	@echo "$(GREEN)Suppression de la base de données...$(NC)"
	$(CONTAINER_BACKEND) python manage.py flush --no-input
	@echo "$(GREEN)Suppression terminée.$(NC)"
	@echo "$(RED)docker compose exec back python manage.py shell -c \"$(NC)"
	@echo "$(RED)from django.db import connection$(NC)"
	@echo "$(RED)with connection.cursor() as c:$(NC)"
	@echo "$(RED)	c.execute('DROP SCHEMA public CASCADE; CREATE SCHEMA public;')$(NC)"
	@echo "$(RED)\"$(NC)"

## —— Migrations  ————————————————————————————————————————————————————————————————
# Création du dossier de sauvegarde s'il n'existe pas
.prepare:
	$(CONTAINER_BACKEND) mkdir -p $(BACKUP_DIR)


update-db:
	@# Help: Met a jour la base de données
	@echo "$(GREEN)Migrations...$(NC)"
	$(CONTAINER_BACKEND) python manage.py makemigrations
	@echo "$(GREEN)Migrate de la base de données...$(NC)"
	$(CONTAINER_BACKEND) python manage.py migrate
	@echo "$(GREEN)Migrations terminées.$(NC)"

## —— Fixtures  ————————————————————————————————————————————————————————————————
fixtures: fixture-create-root fixture-seed-dev fixture-seed-soundboard fixture-tag-playlist fixture-tag-soundboard
	@# Help: Lance l'ensemble des fixtures de développement 

fixture-create-root:
	@# Help: Crée l'utilisateur root — DEBUG=1 requis
	@echo "$(GREEN)Chargement des fixtures de développement...$(NC)"
	$(CONTAINER_BACKEND) python manage.py create_root_user
	@echo "$(GREEN)Fixtures chargées.$(NC)"

fixture-seed-dev:
	@# Help: Crée les données de développement (utilisateur dev + 20 playlists) — DEBUG=1 requis
	@echo "$(GREEN)Chargement des fixtures de développement...$(NC)"
	$(CONTAINER_BACKEND) python manage.py seed_dev
	@echo "$(GREEN)Fixtures chargées.$(NC)"

fixture-seed-soundboard:
	@# Help: Crée les données de développement  — DEBUG=1 requis
	@echo "$(GREEN)Chargement des fixtures de développement...$(NC)"
	$(CONTAINER_BACKEND) python manage.py seed_public_soundboard
	@echo "$(GREEN)Fixtures chargées.$(NC)"

fixture-tag-playlist:
	@# Help: Crée les tags pour les playlists existantes
	@echo "$(GREEN)Création des tags pour les playlists existantes...$(NC)"
	$(CONTAINER_BACKEND) python manage.py seed_playlist_tags
	@echo "$(GREEN)Tags créés.$(NC)"

fixture-tag-soundboard:
	@# Help: Crée les tags pour les soundboards existantes
	@echo "$(GREEN)Création des tags pour les soundboards existantes...$(NC)"
	$(CONTAINER_BACKEND) python manage.py seed_soundboard_tags
	@echo "$(GREEN)Tags créés.$(NC)"

## —— Traductions  ————————————————————————————————————————————————————————————————
trad-init:
	@# Help: Génère les fichiers de traduction (.po) pour toutes les langues
	@echo "$(GREEN)Génération des fichiers de traduction...$(NC)"
	$(CONTAINER_BACKEND) python manage.py makemessages -l fr
	$(CONTAINER_BACKEND) python manage.py makemessages -l en
	@echo "$(GREEN)Fichiers .po générés dans app/locale/$(NC)"


trad-update:
	@# Help: Compile les fichiers de traduction (.po en .mo)
	@echo "$(GREEN)Compilation des fichiers de traduction...$(NC)"
	$(CONTAINER_BACKEND) python manage.py compilemessages
	@echo "$(GREEN)Fichiers .mo compilés et prêts à l'emploi$(NC)"

update-translations:
	@# Help: Met à jour et compile toutes les traductions (makemessages + compilemessages)
	@echo "$(GREEN)Mise à jour complète des traductions...$(NC)"
	$(MAKE) trad-init
	$(MAKE) trad-update
	@echo "$(GREEN)Traductions mises à jour et compilées$(NC)"