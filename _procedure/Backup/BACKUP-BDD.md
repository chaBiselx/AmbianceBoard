# Récupérer / restaurer la base PostgreSQL de production

La base tourne en production dans un conteneur Docker (voir `docker-compose.prod.yml`), **mais le dump se déclenche toujours via `docker compose exec` depuis l'hôte**, pas en se connectant physiquement dans le volume Postgres.

Destination locale visée : `F:\AmbianceBoard\backups-bdd`

---

## 0. Prérequis

- Le disque `F:` monté et accessible en écriture.
- Un accès SSH au serveur de production avec une clé privée.
- Les identifiants de connexion à la base (utilisateur PG, nom de la base) tels que définis dans `docker-compose.prod.yml` / `.env.prod`.

### Variables de session

Les valeurs réelles (hôte, utilisateur, nom de clé, nom de la base) **ne doivent pas être versionnées**. Les définir en début de session dans le terminal WSL :

```bash
export PROD_USER="<utilisateur>"
export PROD_HOST="<ip-ou-domaine>"
export PROD_KEY="$HOME/.ssh/<nom_de_la_cle>"
export PROD_BASE_PATH="<path_du_projet>"
export DB_SERVICE="db"                 # nom du service dans docker-compose.prod.yml
export DB_USER="<user_pg>"
export DB_NAME="<nom_de_la_base>"
export LOCAL_BACKUPS="/mnt/f/AmbianceBoard/backups-bdd"   # F:\AmbianceBoard\backups-bdd
```

### Clé SSH

Comme pour les médias, si la clé a une passphrase, ne la saisir qu'une fois par session :

```bash
eval "$(ssh-agent -s)"
ssh-add "$PROD_KEY"
```

> La passphrase se tape uniquement dans le terminal : jamais dans un script, une variable d'environnement ou ce fichier.

### Contrôle avant transfert

Vérifier la connexion et la taille de la base :

```bash
ssh -i "$PROD_KEY" "$PROD_USER@$PROD_HOST" \
  "cd $PROD_BASE_PATH && docker compose -f docker-compose.prod.yml exec -T $DB_SERVICE \
   psql -U $DB_USER -d $DB_NAME -c \"SELECT pg_size_pretty(pg_database_size('$DB_NAME'));\""
```

Sous WSL, monter le disque si nécessaire :

```bash
sudo mount -t drvfs F: /mnt/f -o metadata,uid=$(id -u),gid=$(id -g),umask=022
```

Créer le dossier de destination :

```bash
mkdir -p "$LOCAL_BACKUPS"
sudo chmod 766 "$LOCAL_BACKUPS"
```

Vérification de la présence du dossier de destination :

```bash
[ -d "$LOCAL_BACKUPS" ] && echo "Existe" || echo "Absent"
```

---

## 1. DUMP

`pg_dump` s'exécute **dans le conteneur** (`docker compose exec`), et le flux de sortie est redirigé directement vers ta WSL/DD via SSH — aucun fichier intermédiaire n'est laissé sur le VPS.

Format recommandé : `-F c` (custom), compressé et compatible restauration sélective avec `pg_restore` :

Le mot de passe est demandé lors du process

```bash
ssh -i "$PROD_KEY" "$PROD_USER@$PROD_HOST" \
  "cd $PROD_BASE_PATH && docker compose -f docker-compose.prod.yml exec -T $DB_SERVICE \
   pg_dump -U $DB_USER -F c $DB_NAME" \
  > "$LOCAL_BACKUPS/${DB_NAME}_$(date +%Y%m%d_%H%M%S).dump"
```

Variante SQL texte (lisible, plus lourd, utile pour un diff ou une relecture rapide) :

```bash
ssh -i "$PROD_KEY" "$PROD_USER@$PROD_HOST" \
  "cd $PROD_BASE_PATH && docker compose -f docker-compose.prod.yml exec -T $DB_SERVICE \
   pg_dump -U $DB_USER $DB_NAME" \
  > "$LOCAL_BACKUPS/${DB_NAME}_$(date +%Y%m%d_%H%M%S).sql"
```

### Exclure des tables du dump

Comme pour `dumpdata` côté Django, `pg_dump` a son propre mécanisme d'exclusion (répétable) :

```bash
ssh -i "$PROD_KEY" "$PROD_USER@$PROD_HOST" \
  "cd $PROD_BASE_PATH && docker compose -f docker-compose.prod.yml exec -T $DB_SERVICE \
   pg_dump -U $DB_USER -F c \
     --exclude-table=django_session \
     --exclude-table=django_admin_log \
     $DB_NAME" \
  > "$LOCAL_BACKUPS/${DB_NAME}_$(date +%Y%m%d_%H%M%S).dump"
```

- `--exclude-table=nom_table` : exclut structure **et** données de la table (le nom accepte les motifs SQL `%`/`_`).
- `--exclude-table-data=nom_table` : garde la structure de la table mais vide son contenu — utile pour des tables de logs volumineuses qu'on veut recréer sans réimporter des millions de lignes.

Options utiles complémentaires :

- `-F c` : format "custom", seul format compatible avec `--exclude-table` combiné à une restauration partielle ultérieure via `pg_restore -t`.
- `-v` : verbeux, utile en cas de gros dump pour suivre la progression via `stderr`.
- `--no-owner --no-privileges` : à ajouter si l'utilisateur PG de destination n'est pas le même que celui de la prod (évite les erreurs `ALTER OWNER` au restore).

> ⚠️ Le dump se fait toujours pendant que les conteneurs tournent normalement (`pg_dump` prend un snapshot cohérent grâce aux transactions MVCC de Postgres). Pas besoin d'arrêter l'application pour un simple backup.

---

## 2. Vérification de l'intégrité

Contrairement à un dossier de fichiers, on ne peut pas comparer des empreintes avant/après : on vérifie plutôt que le dump est exploitable.

```bash
# Taille et présence du fichier
ls -lh "$LOCAL_BACKUPS"/*.dump

# Lister le contenu du dump sans le restaurer (structure + tables incluses)
pg_restore --list "$LOCAL_BACKUPS/${DB_NAME}_<horodatage>.dump"
```

`pg_restore --list` doit afficher la liste des tables attendues (et confirmer l'absence de celles exclues à l'étape 1). Un dump tronqué ou corrompu renvoie une erreur ici plutôt qu'au moment critique de la restauration.

Pour une vérification plus poussée (optionnelle), restaurer le dump dans une base de test locale :

```bash
createdb test_restore
pg_restore -d test_restore "$LOCAL_BACKUPS/${DB_NAME}_<horodatage>.dump"
dropdb test_restore
```

---

## 3. Bonnes pratiques

- **Ne pas arrêter les conteneurs** pour un dump simple : `pg_dump` est cohérent à chaud grâce aux transactions.
- Lancer les dumps volumineux en dehors des heures de pointe.
- Toujours passer par `docker compose exec`, jamais en se connectant directement au volume de données Postgres.
- N'exécuter que des commandes de lecture côté serveur (`pg_dump`, `psql -c "SELECT..."`).
- Ne jamais versionner : adresse du serveur, utilisateur, clé privée, passphrase, identifiants PG, `~/.ssh/config`.
- Utiliser `ssh-agent` plutôt que de stocker la passphrase quelque part.
- Le dump contient des données utilisateurs : chiffrer ou protéger l'accès au disque `F:`.
- **Restaurer les médias et la base au même point dans le temps** (cf. doc `mediafiles`, section restauration) — un dump de base désynchronisé des fichiers médias produit des références orphelines.
- Pour une sauvegarde régulière, planifier la commande de dump (section 1) via le Planificateur de tâches Windows, avec rotation des anciens fichiers (voir script en fin de doc si besoin).

---

## 4. Restauration vers le VPS

Trajet inverse : la source devient le fichier `.dump` sur `F:`, la destination la base du serveur.

> ⚠️ Une restauration complète **écrase** les données de production. Toujours sauvegarder l'existant (4.2) et travailler avec les conteneurs applicatifs arrêtés (4.3) pour éviter toute écriture concurrente pendant le restore.

### 4.1 Préparation WSL

Reprendre les variables de session et l'`ssh-agent` de la section 0, puis vérifier que le disque est bien monté :

```bash
mount | grep -i '/mnt/f'   # doit renvoyer une ligne drvfs
```

### 4.2 Sauvegarder l'existant côté serveur

À faire systématiquement, même si la restauration est urgente.

```bash
ssh -i "$PROD_KEY" "$PROD_USER@$PROD_HOST" \
  "cd $PROD_BASE_PATH && docker compose -f docker-compose.prod.yml exec -T $DB_SERVICE \
   pg_dump -U $DB_USER -F c $DB_NAME" \
  > "/tmp/${DB_NAME}-before-restore-$(date +%Y%m%d-%H%M).dump"
```

(Ce dump de secours peut être fait localement, comme ci-dessus, ou rapatrié ensuite sur le VPS dans `/srv/www/` pour rester cohérent avec la convention du doc `mediafiles`.)

### 4.3 Arrêter les conteneurs applicatifs

Nécessaire pour qu'aucune requête n'écrive pendant le restore. Le conteneur `db` reste up, seuls les conteneurs qui *utilisent* la base sont coupés :

```bash
ssh -i "$PROD_KEY" "$PROD_USER@$PROD_HOST" \
  "cd $PROD_BASE_PATH && docker compose -f docker-compose.prod.yml stop back websocket cronjob"
```

### 4.4 Transfert du fichier de dump vers le VPS

```bash
scp -i "$PROD_KEY" \
  "$LOCAL_BACKUPS/${DB_NAME}_<horodatage>.dump" \
  "$PROD_USER@$PROD_HOST:/tmp/restore.dump"
```

### 4.5 Restauration

Restauration complète, avec `--clean` pour repartir sur un schéma propre (supprime les objets existants avant de les recréer) :

```bash
ssh -i "$PROD_KEY" "$PROD_USER@$PROD_HOST" \
  "cd $PROD_BASE_PATH && docker compose -f docker-compose.prod.yml exec -T $DB_SERVICE \
   pg_restore -U $DB_USER -d $DB_NAME --clean --if-exists /tmp/restore.dump 2>&1 || \
   cat /tmp/restore.dump | docker compose -f docker-compose.prod.yml exec -T $DB_SERVICE \
   pg_restore -U $DB_USER -d $DB_NAME --clean --if-exists"
```

> Selon la config du conteneur, `/tmp/restore.dump` peut ne pas être visible depuis l'intérieur du conteneur `db` (c'est un fichier sur l'hôte, pas dans un volume monté). Solution la plus fiable : streamer le fichier dans le conteneur via `docker compose exec -T` :

```bash
ssh -i "$PROD_KEY" "$PROD_USER@$PROD_HOST" \
  "cd $PROD_BASE_PATH && docker compose -f docker-compose.prod.yml exec -T $DB_SERVICE \
   pg_restore -U $DB_USER -d $DB_NAME --clean --if-exists" \
  < "$LOCAL_BACKUPS/${DB_NAME}_<horodatage>.dump"
```

Cette dernière forme évite complètement le `scp` de l'étape 4.4 : le dump part de ta WSL, transite par le tunnel SSH, et arrive directement dans `pg_restore` sur le VPS.

Restauration **partielle** (une ou quelques tables seulement, ex. pour ré-injecter une table exclue par erreur) :

```bash
ssh -i "$PROD_KEY" "$PROD_USER@$PROD_HOST" \
  "cd $PROD_BASE_PATH && docker compose -f docker-compose.prod.yml exec -T $DB_SERVICE \
   pg_restore -U $DB_USER -d $DB_NAME -t nom_table --clean --if-exists" \
  < "$LOCAL_BACKUPS/${DB_NAME}_<horodatage>.dump"
```

### 4.6 Redémarrer et vérifier

```bash
ssh -i "$PROD_KEY" "$PROD_USER@$PROD_HOST" \
  "cd $PROD_BASE_PATH && docker compose -f docker-compose.prod.yml up -d"

ssh -i "$PROD_KEY" "$PROD_USER@$PROD_HOST" \
  "cd $PROD_BASE_PATH && docker compose -f docker-compose.prod.yml exec -T $DB_SERVICE \
   psql -U $DB_USER -d $DB_NAME -c \"SELECT pg_size_pretty(pg_database_size('$DB_NAME'));\""
```

Terminer par un contrôle fonctionnel dans l'application : connexion utilisateur, lecture de données restaurées, cohérence avec les médias restaurés au même point dans le temps (section 4 du doc `mediafiles`).

### 4.7 Nettoyage

Une fois la restauration validée, et seulement après :

```bash
ssh -i "$PROD_KEY" "$PROD_USER@$PROD_HOST" "rm -f /tmp/restore.dump"
ssh -i "$PROD_KEY" "$PROD_USER@$PROD_HOST" "ls -lh /tmp/${DB_NAME}-before-restore-*.dump"
```

Conserver le dump de secours (4.2) quelques jours avant de le supprimer.

### Points de vigilance

- Ne jamais lancer `--clean` en restauration sans avoir fait le dump de secours de l'étape 4.2.
- Vérifier que `$DB_SERVICE`, `$DB_USER` et `$DB_NAME` correspondent bien à `docker-compose.prod.yml` / `.env.prod` avant de lancer quoi que ce soit en écriture.
- Restaurer la base **et** les médias au même point dans le temps (cf. doc `mediafiles`).
- Si des tables ont été exclues au dump (section 1), les considérer comme volontairement absentes après restore — ne pas s'étonner de leur vide.
