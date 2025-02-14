# Variables
BACKUP_DIR=backup
MEDIA_FOLDER=mediafiles
MEDIA_BACKUP=$(BACKUP_DIR)/media_backup.tar.gz
DATA_BACKUP=$(BACKUP_DIR)/data.json
LOG_DIR=./logs
 

 
# Dump des données et des fichiers médias
dump: 
	@# Help: Exporte la base de données et les fichiers médias afin de pouvoir les restaurer plus tard
	$(MAKE) .prepare
	@echo "$(GREEN)Sauvegarde de la base de données...$(NC)"
	python manage.py dumpdata --exclude contenttypes --exclude auth.permission > $(DATA_BACKUP)
	@echo "$(GREEN)Sauvegarde des fichiers médias...$(NC)"
	tar -czf $(MEDIA_BACKUP) $(MEDIA_FOLDER)/
	@echo "$(GREEN)Dump terminé : $(DATA_BACKUP) et $(MEDIA_BACKUP)$(NC)"
 
# Chargement des données et des fichiers médias
load: 
	@# Help: Restaure la base de données et les fichiers médias
	$(MAKE) .prepare
	@echo "$(GREEN)Migrate de la base de données...$(NC)"
	python manage.py migrate
	@echo "$(GREEN)Restauration des fichiers médias...$(NC)"
	tar -xzf $(MEDIA_BACKUP)
	@echo "$(GREEN)Restauration de la base de données...$(NC)"
	python manage.py loaddata $(DATA_BACKUP)
	@echo "$(GREEN)Restauration terminée.$(NC)"

#nettoyage des fichier de logs
clean:
	@# Help: vide les fichiers de logs sans les supprimer
	@find $(LOG_DIR) -type f -name "*.log" -exec sh -c '>'{}'; echo "Logs vidés pour {}"' \;

 
# Création du dossier de sauvegarde s'il n'existe pas
.prepare:
	mkdir -p $(BACKUP_DIR)


update-db:
	@# Help: Met a jour la base de données
	@echo "$(GREEN)Migrations...$(NC)"
	python manage.py makemigrations
	@echo "$(GREEN)Migrate de la base de données...$(NC)"
	python manage.py migrate
	@echo "$(GREEN)Migrations terminées.$(NC)"