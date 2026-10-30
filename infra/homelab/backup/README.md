# Sauvegarde de la production vers le homelab

Script Linux qui automatise la recuperation decrite dans
[BACKUP-BDD.md](../../../_procedure/BACKUP-BDD.md) et
[BACKUP-MEDIAFILES.md](../../../_procedure/BACKUP-MEDIAFILES.md) (sections 0 a 2).
Il ne fait que des lectures cote serveur ; la restauration reste manuelle.

## Organisation

| Fichier | Role |
|---|---|
| `script/backup-homelab.sh` | Point d'entree : variables, options, enchainement |
| `script/lib/common.sh` | Journalisation et controles generiques |
| `script/lib/backup-db.sh` | Dump PostgreSQL et verification |
| `script/lib/backup-media.sh` | Synchronisation et verification des medias |
| `script/lib/transports/ssh.sh` | Acces au serveur (ssh + rsync) |
| `backup.env.example` | Modele de configuration |

## Configuration

```bash
cp backup.env.example backup.env
chmod 600 backup.env
```

Les variables peuvent aussi etre exportees dans le shell, comme dans les
procedures. `BACKUP_ENV_FILE` permet d'utiliser un autre fichier.
Les valeurs ne doivent pas contenir d'espaces.

La passphrase de la cle n'est jamais lue par le script : la charger avant via
`eval "$(ssh-agent -s)" && ssh-add "$PROD_KEY"`. Pour un cron, utiliser une cle
dediee ou un agent persistant.

## Utilisation

```bash
./script/backup-homelab.sh --dry-run          # simulation
./script/backup-homelab.sh                    # base + medias
./script/backup-homelab.sh --verify           # + controle md5 des medias
./script/backup-homelab.sh --db-only
./script/backup-homelab.sh --media-only --delete
```

## Transports

`TRANSPORT` choisit le fichier `script/lib/transports/<nom>.sh`. A travers un
VPN, le transport `ssh` suffit : renseigner `PROD_HOST` avec l'adresse VPN du
serveur. Un autre mode d'acces s'ajoute avec un nouveau fichier qui definit :

- `transport_check` : verifie configuration et connexion ;
- `transport_exec "<commande>"` : execute une commande sur le serveur ;
- `transport_sync <distant> <local> [options rsync]` : copie un dossier.
