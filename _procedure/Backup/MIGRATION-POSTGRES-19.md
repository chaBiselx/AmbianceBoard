# Sauvegarde et migration PostgreSQL 15 vers 19

Cette procédure prépare une sauvegarde complète de la base applicative avant
la migration de PostgreSQL 15.8 vers 19. Elle conserve les données PostgreSQL
15 séparément pour permettre un retour arrière. Prévoir une interruption du
service et tester d'abord la procédure sur une copie isolée.

Pour les sauvegardes régulières, voir [BACKUP-BDD.md](BACKUP-BDD.md), le
[script homelab](../../infra/homelab/backup/README.md) et
[SYSTEMD_TIMER.md](SYSTEMD_TIMER.md). Le script peut exclure des tables :
ne pas utiliser un dump avec exclusions pour cette migration.

## 1. Préparer l'intervention

- Effectuer les commandes sur l'hôte Docker, depuis la racine du dépôt, avec
  les droits d'accès à Docker. Choisir le bon environnement Compose et sa
  configuration habituelle ; ne pas afficher ni copier les secrets.
- Vérifier l'espace disponible pour les dumps, l'ancien répertoire de données
  et le nouveau. Les sauvegardes contiennent des données utilisateurs et
  potentiellement des mots de passe de rôles : utiliser un stockage protégé,
  chiffré et hors du dépôt, avec une copie indépendante.
- Identifier toutes les bases, rôles, extensions, tablespaces et configurations
  personnalisées à conserver. `pg_dump` ne sauvegarde qu'une base ; les médias
  sont séparés. Prévoir aussi leur sauvegarde cohérente au même point dans le
  temps : [BACKUP-MEDIAFILES.md](BACKUP-MEDIAFILES.md).
- Vérifier la compatibilité des extensions, des applications et des locales
  avec PostgreSQL 19. Les tablespaces et paramètres personnalisés nécessitent
  une préparation spécifique non couverte par cet exemple.
- Tester une restauration complète dans un environnement isolé avant toute
  intervention en production. La liste d'un dump ne prouve pas sa restauration.

Les commandes suivantes utilisent Bash. En développement :

```bash
COMPOSE=(docker compose -f docker-compose.yml)
```

En production, utiliser à la place :

```bash
COMPOSE=(docker compose -f docker-compose.prod.yml)
```

Exécuter les commandes avec la même configuration d'environnement Compose
que celle utilisée normalement pour cet environnement. Vérifier la version
effective avant de continuer :

```bash
"${COMPOSE[@]}" exec -T db postgres --version
```

Le reste de cette procédure suppose PostgreSQL 15 comme source, une base
applicative et un répertoire cible PostgreSQL 19 neuf. Adapter la sauvegarde
et la restauration si d'autres bases ou rôles existent.

## 2. Interrompre les écritures et sauvegarder

Arrêter les services applicatifs, sans arrêter `db` :

```bash
"${COMPOSE[@]}" stop back websocket cronjob celery celery-music-labeler
```

Bloquer aussi les éventuels clients externes, tâches ou connexions non gérés
par Compose. Aucune écriture ne doit reprendre avant la bascule ou le retour
arrière. Un simple backup régulier peut être effectué à chaud, mais une
migration nécessite ce gel pour ne pas perdre les écritures après le dump.

Choisir un dossier de sauvegarde existant, sécurisé et situé hors du dépôt.
Créer un sous-dossier unique et privé :

```bash
umask 077
mkdir -p /srv/www/backup/pg15-XXXXXX
BACKUP_DIR="$(mktemp -d /srv/www/backup/pg15-XXXXXX)"
```

Remplacer `/chemin/securise` avant exécution. Le dossier créé ne doit pas être
accessible publiquement. Sauvegarder la base configurée et les objets globaux
(notamment les rôles) :

```bash
"${COMPOSE[@]}" exec -T db sh -c \
  'exec pg_dump -U "$POSTGRES_USER" -Fc "$POSTGRES_DB"' \
  > "$BACKUP_DIR/base.dump"

"${COMPOSE[@]}" exec -T db sh -c \
  'exec pg_dumpall -U "$POSTGRES_USER" --globals-only' \
  > "$BACKUP_DIR/globals.sql"
```

Contrôler le code de sortie de **chaque commande** : en cas d'erreur, ne pas
utiliser le fichier produit, résoudre le problème et recommencer. `globals.sql`
peut contenir des empreintes de mots de passe ; ne pas l'afficher ni le
versionner. Sauvegarder séparément toute autre base et les configurations non
couvertes par les dumps.

Vérifier au minimum que le dump est lisible :

```bash
test -s "$BACKUP_DIR/base.dump"
test -s "$BACKUP_DIR/globals.sql"
"${COMPOSE[@]}" exec -T db pg_restore --list \
  < "$BACKUP_DIR/base.dump" > /dev/null
```

Chaque commande doit réussir. Tester ensuite la restauration complète sur une
instance isolée avec les rôles et extensions requis. Une vérification
`--list` seule ne détecte pas nécessairement toutes les corruptions.

## 3. Préparer PostgreSQL 19

Arrêter la base 15 seulement après avoir vérifié la sauvegarde :

```bash
"${COMPOSE[@]}" stop db
```

Conserver intact le dossier existant `./db-data/`. Ne pas le supprimer, le
vider ou le monter comme répertoire de données PostgreSQL 19 : les formats
des versions majeures ne sont pas compatibles.

Dans le fichier Compose choisi, remplacer l'image et le montage du service
`db` par les valeurs suivantes :

```yaml
image: postgres:19.0-trixie@sha256:4ea94de574c17f0372722806c949757050fbb1cd7648410fe45d6bba275cc00e
volumes:
  - ./db-data-pg19:/var/lib/postgresql
```

Le chemin `./db-data-pg19` doit être **nouveau et vide**. Préserver les autres
paramètres du service. Depuis PostgreSQL 18, l'image officielle utilise par
défaut `/var/lib/postgresql/19/docker` pour PostgreSQL 19 et le volume doit
être monté sur `/var/lib/postgresql`. Ne pas conserver le montage 15 sur
`/var/lib/postgresql/data` : les données 19 pourraient être écrites ailleurs.
Modifier séparément [docker-compose.yml](../../docker-compose.yml) et
[docker-compose.prod.yml](../../docker-compose.prod.yml) si les deux
environnements doivent être migrés ; leurs données restent indépendantes.

Démarrer uniquement la nouvelle base, puis attendre qu'elle soit prête :

```bash
"${COMPOSE[@]}" up -d --no-deps db
"${COMPOSE[@]}" exec -T db sh -c \
  'exec pg_isready -U "$POSTGRES_USER" -d "$POSTGRES_DB"'
"${COMPOSE[@]}" exec -T db postgres --version
```

Vérifier que la version est bien 19 et que le stockage effectif correspond
au nouveau montage avant de restaurer. Si la base n'est pas prête, attendre
et vérifier les journaux côté administrateur avant de poursuivre.

## 4. Restaurer et contrôler

L'initialisation de l'image crée le superutilisateur et la base définis par
`POSTGRES_USER` et `POSTGRES_DB` si le répertoire est vide. Avant restauration,
recréer les autres rôles et tablespaces nécessaires à partir de la sauvegarde
globale, et installer les extensions requises. Ne pas rejouer aveuglément
`globals.sql` : il peut tenter de recréer le superutilisateur déjà initialisé.
Préserver les propriétaires, droits, locales et paramètres requis ; traiter
explicitement les éventuels conflits sur une instance de test.

Pour restaurer le dump de la base applicative dans la base neuve :

```bash
"${COMPOSE[@]}" exec -T db sh -c \
  'exec pg_restore --exit-on-error -U "$POSTGRES_USER" -d "$POSTGRES_DB"' \
  < "$BACKUP_DIR/base.dump"
```

Cette commande suppose que la base cible est vide et que tous les rôles et
extensions nécessaires sont disponibles. En cas d'erreur, arrêter : la
restauration peut être partielle. Corriger la cause et recommencer dans une
base neuve ; ne pas relancer sur une base partiellement restaurée.

Avant de rouvrir les écritures, contrôler la version, les objets, les droits,
les extensions et la cohérence des données et médias, puis tester les parcours
applicatifs et les migrations Django dans un environnement isolé. Redémarrer
ensuite les services de l'environnement selon la procédure habituelle et
vérifier leur état. Conserver les sauvegardes et les données 15 selon la
politique de rétention.


### puge 

Dans le cas de réussite, supprimer le dossier de backup ainsi que l'anciend dossier de base de données. 

```bash
sudo rm -rf db-data
sudo rm -rf /srv/www/backup
```


## 5. Retour arrière

Avant toute écriture sur PostgreSQL 19, arrêter les services applicatifs et la
base 19, rétablir l'image PostgreSQL 15 d'origine et le montage
`./db-data/:/var/lib/postgresql/data/`, puis redémarrer et vérifier l'ancienne
base avant les services applicatifs. Ne pas modifier le répertoire 15 conservé.

Après reprise des écritures sur PostgreSQL 19, ce retour arrière ne contient
pas les nouvelles données. Arrêter les écritures et définir une migration
inverse ou une stratégie de récupération avant de revenir en arrière.

Références : [mise à niveau PostgreSQL](https://www.postgresql.org/docs/19/upgrading.html),
[répertoire de données de l'image officielle](https://github.com/docker-library/docs/blob/master/postgres/README.md#pgdata).
