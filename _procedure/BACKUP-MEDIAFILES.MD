# Récupérer le dossier `mediafiles` de la production vers le disque `F:`

Le dossier des médias en production se trouve sur le serveur dans :



Il est monté dans les conteneurs sur `/usr/src/app/mediafiles/` (voir `docker-compose.prod.yml`), mais **la copie se fait toujours depuis l'hôte**, pas depuis le conteneur.

Destination locale visée : `F:\AmbianceBoard\mediafiles`

---

## 0. Prérequis

- Le disque `F:` monté et accessible en écriture.
- `rsync` (via WSL) pour la reprise sur incident.
- Un accès SSH au serveur de production avec une clé privée.

### Variables de session

Les valeurs réelles (hôte, utilisateur, nom de clé) **ne doivent pas être versionnées**. Les définir en début de session dans le terminal WSL :

```bash
export PROD_USER="<utilisateur>"
export PROD_HOST="<ip-ou-domaine>"
export PROD_KEY="$HOME/.ssh/<nom_de_la_cle>"
export PROD_BASE_PATH="<path_du_projet>"
export PROD_MEDIA="$PROD_BASE_PATH/mediafiles"
export LOCAL_MEDIA="/mnt/f/AmbianceBoard/mediafiles"   # F:\AmbianceBoard\mediafiles
```



### Clé SSH

La clé est protégée par une **passphrase**, demandée à chaque connexion. Pour ne la saisir qu'une seule fois sur toute la session (`rsync` ouvre plusieurs connexions) :

```bash
eval "$(ssh-agent -s)"
ssh-add "$PROD_KEY"
```

> La passphrase se tape uniquement dans le terminal : jamais dans un script, une variable d'environnement ou ce fichier.

### Contrôle avant transfert

Vérifier la connexion, la taille et le nombre de fichiers :

```bash
ssh -i "$PROD_KEY" "$PROD_USER@$PROD_HOST" \
  "du -sh $PROD_MEDIA && find $PROD_MEDIA -type f | wc -l"
```

Sous Wsl il faut monter le disque du si necessaire 

Créer le dossier de destination :
```bash
sudo mount -t drvfs F: /mnt/f -o metadata,uid=$(id -u),gid=$(id -g),umask=022

```

```bash
mkdir -p "$LOCAL_MEDIA"
sudo chmod 766 /mnt/f/AmbianceBoard/mediafiles
```


Vérification de la présence du dossier de destination : 
```bash
[ -d "$LOCAL_MEDIA" ] && echo "Existe" || echo "Absent"
```


---

## 1 RSYNC

`rsync` est la meilleure option : il est reprenable, incrémental et compresse le transfert.

Depuis un terminal WSL/ou Linux :

Simulation à faire une première fois (aucune écriture grâce au `-n`) :

```bash
rsync -avzn --progress \
  -e "ssh -i $PROD_KEY" \
  "$PROD_USER@$PROD_HOST:$PROD_MEDIA/" \
  "$LOCAL_MEDIA/"
```

Transfert réel :

```bash
rsync -avz --progress --partial \
  -e "ssh -i $PROD_KEY" \
  "$PROD_USER@$PROD_HOST:$PROD_MEDIA/" \
  "$LOCAL_MEDIA/"
```

Options utiles :

- `-a` : mode archive (récursif,  identique à -rlptgoD (pas -H)).
- `-v` : verbeux.
- `-z` : compression pendant le transfert.
- `--progress` : barre de progression par fichier.
- `--partial` : conserve les fichiers partiels pour permettre la reprise.
- `--delete` : (optionnel) supprime en local les fichiers absents de la prod → miroir exact.
- `-n` / `--dry-run` : simulation.

> ⚠️ Le `/` final sur la source (`mediafiles/`) est important : il copie le **contenu** du dossier. Sans ce `/`, rsync crée un sous-dossier `mediafiles` supplémentaire.

Relancer exactement la même commande en cas de coupure : seuls les fichiers manquants ou modifiés seront retransférés.

---

## 2. Vérification de l'intégrité

```bash
# Empreintes côté serveur
ssh -i "$PROD_KEY" "$PROD_USER@$PROD_HOST" \
  "cd $PROD_MEDIA && find . -type f -exec md5sum {} + | sort -k2" > /tmp/remote.md5

# Empreintes côté local
(cd "$LOCAL_MEDIA" && find . -type f -exec md5sum {} + | sort -k2) > /tmp/local.md5

diff /tmp/remote.md5 /tmp/local.md5 && echo "OK : contenus identiques"
```

---

## 3. Bonnes pratiques

- **Ne pas arrêter les conteneurs** : la copie en lecture seule du dossier est sans impact sur la prod.
- Lancer les gros transferts en dehors des heures de pointe.
- Ne jamais copier vers/depuis l'intérieur d'un conteneur : le volume hôte `./mediafiles` est la source de vérité.
- N'exécuter que des commandes de lecture sur le serveur (`du`, `find`, `md5sum`, `rsync` côté source).
- Ne jamais versionner : adresse du serveur, utilisateur, clé privée, passphrase, `~/.ssh/config`.
- Utiliser `ssh-agent` plutôt que de stocker la passphrase quelque part.
- Les médias contiennent des données utilisateurs : chiffrer ou protéger l'accès au disque `F:` si la sauvegarde est conservée.
- Pour une sauvegarde régulière, planifier la commande `rsync` (section 1) via le Planificateur de tâches Windows.

---

## 4. Restauration vers le VPS

Trajet inverse : la source devient le disque `F:`, la destination le serveur.

> ⚠️ Deux pièges spécifiques : NTFS n'a conservé aucun propriétaire ni permission Linux (à réappliquer en étape 4.5), et les chemins des médias sont référencés en base de données — restaurer `mediafiles` sans un dump de base du même moment produit des références orphelines.

Les conteneurs tournent sous `appuser` **uid/gid 1000** (voir `app/Dockerfile.prod`), et `./mediafiles` est monté dans `back`, `websocket` et `cronjob`.

### 4.1 Préparation WSL 

Reprendre les variables de session et l'`ssh-agent` de la section 0, puis vérifier que le disque est bien monté :

```bash
mount | grep -i '/mnt/f'   # doit renvoyer une ligne drvfs
```

### 4.2 Sauvegarder l'existant côté serveur

À faire systématiquement, même si le dossier semble vide ou corrompu.

```bash
ssh -i "$PROD_KEY" "$PROD_USER@$PROD_HOST" \
  "df -h /srv && tar -czf /srv/www/mediafiles-before-restore-\$(date +%Y%m%d-%H%M).tar.gz -C $PROD_BASE_PATH mediafiles"
```

Le `df -h` vérifie d'abord qu'il reste la place pour l'archive.

### 4.3 Arrêter les conteneurs

Nécessaire uniquement pour une restauration complète, afin qu'aucun upload ni le cron n'écrive pendant la copie.

```bash
ssh -i "$PROD_KEY" "$PROD_USER@$PROD_HOST" \
  "cd $PROD_BASE_PATH && docker compose -f docker-compose.prod.yml down"
```

### 4.4 Transfert

Simulation d'abord, à relire attentivement :

```bash
rsync -rvzn --progress \
  --no-perms --no-owner --no-group --omit-dir-times \
  -e "ssh -i $PROD_KEY" \
  "$LOCAL_MEDIA/" \
  "$PROD_USER@$PROD_HOST:$PROD_MEDIA/"
```

Transfert réel, mode additif (n'efface rien en prod) :

```bash
rsync -rvz --progress --partial \
  --no-perms --no-owner --no-group --omit-dir-times \
  -e "ssh -i $PROD_KEY" \
  "$LOCAL_MEDIA/" \
  "$PROD_USER@$PROD_HOST:$PROD_MEDIA/"
```

Mode miroir exact — **destructif**, supprime en prod tout ce qui n'est pas dans la sauvegarde. À n'utiliser qu'après l'étape 4.2 et une simulation relue :

```bash
rsync -rvz --progress --partial --delete \
  --no-perms --no-owner --no-group --omit-dir-times \
  -e "ssh -i $PROD_KEY" \
  "$LOCAL_MEDIA/" \
  "$PROD_USER@$PROD_HOST:$PROD_MEDIA/"
```

### 4.5 Rétablir les droits — étape obligatoire

Sans cette étape, Django ne peut ni lire ni écrire les médias et les uploads échouent. 


Id:1000 utilisateur dans /app/dockerfile.prod
```bash
ssh -i "$PROD_KEY" "$PROD_USER@$PROD_HOST" "
  chown -R 1000:1000 $PROD_MEDIA &&
  find $PROD_MEDIA -type d -exec chmod 755 {} + &&
  find $PROD_MEDIA -type f -exec chmod 644 {} +
"
```

Le `-type d` / `-type f` cible des objets différents : `755` sur les **dossiers**, `644` sur les **fichiers**. Sur un dossier, le bit `x` sert à le *traverser* — un dossier en `644` rend ses fichiers inaccessibles même s'ils sont lisibles, et nginx (qui sert `/media/` en direct) renvoie alors des 403.

Ces `chmod` sont idempotents : ils ne changent rien si la prod est déjà correcte. Ils servent de filet après une restauration depuis NTFS, qui ne stocke aucune permission POSIX et peut faire propager des modes aberrants par rsync.

### 4.6 Redémarrer et vérifier

```bash
ssh -i "$PROD_KEY" "$PROD_USER@$PROD_HOST" \
  "cd $PROD_BASE_PATH && docker compose -f docker-compose.prod.yml up -d"

ssh -i "$PROD_KEY" "$PROD_USER@$PROD_HOST" \
  "du -sh $PROD_MEDIA && find $PROD_MEDIA -type f | wc -l && ls -l $PROD_MEDIA"

find "$LOCAL_MEDIA" -type f | wc -l
```

La comparaison stricte par empreintes de la section 2 reste valable telle quelle.

Terminer par un contrôle fonctionnel : lecture d'une musique et affichage des icônes de soundboard/playlist depuis l'application.

### 4.7 Nettoyage

Une fois la restauration validée, et seulement après :

```bash
ssh -i "$PROD_KEY" "$PROD_USER@$PROD_HOST" "ls -lh /srv/www/mediafiles-before-restore-*.tar.gz"
```

Conserver l'archive quelques jours avant de la supprimer.

### Points de vigilance

- Ne jamais lancer `--delete` sans la simulation 4.4 et l'archive 4.2.
- Ne pas oublier le `chown` de l'étape 4.5 : c'est la cause d'erreur la plus fréquente après une restauration.
- Restaurer les médias **et** la base au même point dans le temps.
- Le `/` final sur `$LOCAL_MEDIA/` reste indispensable, sinon rsync crée `mediafiles/mediafiles` sur le serveur.
