# Planifier des backups avec cron sous un utilisateur Linux
 
Guide pour exécuter des commandes de sauvegarde via `cron` avec un utilisateur dédié (principe du moindre privilège).
 
---
 
## 1. Prérequis
 
- Une distribution Linux avec `cron` installé et actif
- Un accès `root` ou `sudo`
```bash
# Debian / Ubuntu
sudo apt update && sudo apt install -y cron rsync
sudo systemctl enable --now cron

```


## Créer un utilisateur local 

voir [Ajouter User](../Account/ADD-USER.md )
et definir un Mot de passe 

```bash
sudo useradd -m cron_user_local
sudo passwd cron_user_local
```


donner les droits pour le dossier des backups
```bash
sudo chown -R cron_user_local:cron_user_local /var/backup/AmbianceBoard
```

## définir les secrets en local (user)

