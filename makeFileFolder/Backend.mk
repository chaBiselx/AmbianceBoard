# Variables
BACKUP_DIR=./backup
MEDIA_FOLDER=./mediafiles
MEDIA_BACKUP=$(BACKUP_DIR)/media_backup.tar.gz
DATA_BACKUP=$(BACKUP_DIR)/data.json
LOG_DIR=./logs

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

# Traductions
makemessages:
	@# Help: Génère les fichiers de traduction (.po) pour toutes les langues
	@echo "$(GREEN)Génération des fichiers de traduction...$(NC)"
	$(CONTAINER_BACKEND) python manage.py makemessages -l fr
	$(CONTAINER_BACKEND) python manage.py makemessages -l en
	@echo "$(GREEN)Fichiers .po générés dans app/locale/$(NC)"


compilemessages:
	@# Help: Compile les fichiers de traduction (.po en .mo)
	@echo "$(GREEN)Compilation des fichiers de traduction...$(NC)"
	$(CONTAINER_BACKEND) python manage.py compilemessages
	@echo "$(GREEN)Fichiers .mo compilés et prêts à l'emploi$(NC)"

update-translations:
	@# Help: Met à jour et compile toutes les traductions (makemessages + compilemessages)
	@echo "$(GREEN)Mise à jour complète des traductions...$(NC)"
	$(MAKE) makemessages
	$(MAKE) compilemessages
	@echo "$(GREEN)Traductions mises à jour et compilées$(NC)"