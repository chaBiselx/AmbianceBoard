# Planifier des backups avec systemd sous un utilisateur Linux
 
Avantage : 

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
sudo -A setfacl -R -m u:cron_user_local:rwx /var/backup/AmbianceBoard
```

## définir les secrets en local (user)

`cron_user_local`. Il ne configure pas le poste depuis lequel ce document est
lu. Il nécessite systemd 256 ou plus pour `systemd-creds --user`, un
gestionnaire systemd utilisateur fonctionnel et un stockage persistant pour
la clé de chiffrement systemd. Vérifier la version sur le poste cible avec
`systemd-creds --version`. Si le chiffrement ou le chargement exige une
autorisation, la configuration doit être adaptée par l'administrateur.

Activer le linger pour que le gestionnaire utilisateur puisse fonctionner sans
session ouverte et redémarre après un reboot :

```bash
sudo loginctl enable-linger cron_user_local
```

Les étapes suivantes sont exécutées sur le poste cible en tant que
`cron_user_local`. Le dépôt et le script doivent y être présents.

### 1. Variables persistantes non secrètes

passer via cron_user_local
```bash
sudo -i -u cron_user_local
```

ou avec bash 
```bash
sudo -u cron_user_local -s /bin/bash
```

Créer le répertoire :

```bash
mkdir -p ~/.config/ambianceboard
chmod 700 ~/.config/ambianceboard
```

Créer ensuite `~/.config/ambianceboard/backup.env` avec les valeurs adaptées
au poste cible. Ce fichier est commun aux shells et au service : utiliser des
valeurs littérales sans espaces, sans `export` ni expansion de variables.

```ini
XDG_RUNTIME_DIR="/run/user/$(id -u)"
DBUS_SESSION_BUS_ADDRESS="unix:path=$XDG_RUNTIME_DIR/bus"

PROD_USER=user_backup_cron
PROD_BASE_PATH=/srv/www/AmbianceBoard
PROD_MEDIA=/srv/www/AmbianceBoard/mediafiles
LOCAL_MEDIA=/var/backup/AmbianceBoard/mediafiles
LOCAL_BACKUPS=/var/backup/AmbianceBoard/backups-bdd
DB_SERVICE=db
```

Le dossier et le fichier doivent rester dans le répertoire personnel persistant
du compte. Protéger les permissions du fichier :

```bash
chmod 600 ~/.config/ambianceboard/backup.env
```

Pour les sessions Bash, ajouter ce bloc à `~/.profile` et à `~/.bashrc`, sans
remplacer leur contenu existant :

```bash
if [ -f "$HOME/.config/ambianceboard/backup.env" ]; then
    set -a
    . "$HOME/.config/ambianceboard/backup.env"
    set +a
fi
```

Ouvrir une nouvelle session pour prendre en compte les modifications. Les
shells de connexion et les shells Bash interactifs chargent respectivement
ces fichiers selon leur configuration. Les autres shells et programmes ne
reçoivent pas nécessairement ces variables : configurer leur environnement
séparément si nécessaire. Le service ci-dessous lit directement le même
fichier, sans dépendre d'une session interactive.

### 2. Secrets chiffrés

`DB_USER`, `DB_NAME` et `PROD_HOST` sont traités comme des informations
sensibles dans ce POC. `PROD_KEY` est un chemin, pas la clé elle-même : pour
protéger la clé privée, chiffrer son **contenu** et fournir au script le
chemin du credential déchiffré.

Créer le répertoire, puis saisir les trois valeurs sans les placer dans
l'historique du shell :

```bash
mkdir -p ~/.config/secrets
chmod 700 ~/.config/secrets
(
    set -o pipefail
    for nom in db_user db_name prod_host; do
        if ! read -r -s -p "Valeur de $nom : " valeur </dev/tty; then
            printf '\nÉchec de la lecture de %s\n' "$nom" >&2
            exit 1
        fi
        printf '\n'
        if [ -z "$valeur" ]; then
            printf 'Valeur vide refusée pour %s\n' "$nom" >&2
            exit 1
        fi
        tmp=$(mktemp "$HOME/.config/secrets/.${nom}.XXXXXX") || exit 1
        trap 'rm -f -- "$tmp"' EXIT
        if ! printf '%s' "$valeur" |
            systemd-creds encrypt --user --name="$nom" - - > "$tmp"; then
            printf 'Échec de la création de %s\n' "$nom" >&2
            exit 1
        fi
        unset valeur
        chmod 600 "$tmp" && mv -f -- "$tmp" "$HOME/.config/secrets/$nom.cred" || exit 1
        trap - EXIT
    done
)
```

Vérifier que les trois commandes ont réussi avant de continuer. En cas
d'échec, corriger la cause et recréer le credential concerné. Ne pas utiliser
`--with-key=null`, qui ne protège pas la confidentialité.

Si le service signale `variables manquantes : DB_USER`, vérifier le contenu
du credential sans l'afficher :

```bash
if valeur=$(systemd-creds decrypt --user --name=db_user \
    "$HOME/.config/secrets/db_user.cred" -); then
    if [ -n "$valeur" ]; then
        echo "Credential non vide"
    else
        echo "Credential vide"
    fi
else
    echo "Échec du déchiffrement"
fi
unset valeur
```

Si le credential est vide, reprendre le bloc de création ci-dessus en
remplaçant `for nom in db_user db_name prod_host; do` par
`for nom in db_user; do` et saisir le nom de l'utilisateur PostgreSQL.
Le nouveau credential remplace l'ancien uniquement après un chiffrement
réussi. Vérifier à nouveau qu'il n'est pas vide, puis relancer le service.

Chiffrer ensuite la clé privée déjà installée sur le poste cible :

```bash
systemd-creds encrypt --user --name=prod_key \
    "$HOME/.ssh/id_ed25519_ambianceboard_cron" \
    "$HOME/.config/secrets/prod_key.cred"
chmod 600 ~/.config/secrets/*.cred
```

Le fichier source de la clé reste présent et doit aussi être protégé. Les
credentials sont liés au poste et au compte : prévoir une procédure de
récupération sécurisée avant une migration, réinstallation ou modification
de l'identité du compte. Ils ne protègent pas contre root ou un processus
ayant accès au compte. Pour une exécution sans interaction, SSH doit pouvoir
utiliser la clé sans demander de passphrase ni de confirmation de clé hôte ;
préparer un accès dédié et vérifier l'identité du serveur au préalable.

### 3. Vérification SSH et agent utilisateur

Depuis une session de `cron_user_local`, vérifier l'identité du serveur avec la
même adresse que `PROD_HOST` :

```bash
mkdir -p ~/.config/systemd/user
```

Pour rendre l'agent accessible au service après déconnexion, créer
`~/.config/systemd/user/ssh-agent.service` :



```ini
[Unit]
Description=Agent SSH utilisateur

[Service]
Type=simple
ExecStart=/usr/bin/ssh-agent -D -a %t/ambianceboard-ssh-agent.sock
Restart=on-failure

[Install]
WantedBy=default.target
```

Dans une session disposant de l'accès au gestionnaire systemd utilisateur :

```bash
systemctl --user daemon-reload
systemctl --user enable --now ssh-agent.service
export SSH_AUTH_SOCK="${XDG_RUNTIME_DIR:-/run/user/$(id -u)}/ambianceboard-ssh-agent.sock"
ssh-add ~/.ssh/id_ed25519_ambianceboard_cron
ssh-add -l
```

Saisir la passphrase directement dans le terminal. Avec le linger activé,
l'agent peut rester actif après déconnexion, mais les clés chargées sont
perdues au redémarrage de la machine ou de l'agent : relancer `ssh-add` après
chaque redémarrage. Le timer peut échouer tant que la clé n'est pas chargée.
Un processus ayant accès au socket peut demander à l'agent d'utiliser la clé.

### 4. Service utilisateur

Créer le répertoire `~/.config/systemd/user` si nécessaire, puis créer
`~/.config/systemd/user/cron_job.service`. Remplacer le chemin de
`ExecStart` par le chemin **local absolu** du script sur le poste cible ; le
chemin de production `PROD_BASE_PATH` désigne quant à lui le serveur distant.


```bash
mkdir -p ~/.config/systemd/user
mkdir -p ~/.cache/ambianceboard-backup
chmod 700 ~/.cache/ambianceboard-backup
```

Modifier le fichier `~/.config/systemd/user/cron_job.service` :


```ini
[Unit]
Description=Sauvegarde AmbianceBoard
Requires=ssh-agent.service
After=ssh-agent.service

[Service]
Type=oneshot
EnvironmentFile=%h/.config/ambianceboard/backup.env
Environment=TMPDIR=%h/.cache/ambianceboard-backup
Environment=SSH_AUTH_SOCK=%t/ambianceboard-ssh-agent.sock
LoadCredentialEncrypted=db_user:%h/.config/secrets/db_user.cred
LoadCredentialEncrypted=db_name:%h/.config/secrets/db_name.cred
LoadCredentialEncrypted=prod_host:%h/.config/secrets/prod_host.cred
LoadCredentialEncrypted=prod_key:%h/.config/secrets/prod_key.cred
ExecStart=/bin/bash -c 'set -eu; DB_USER=$$(cat "$$CREDENTIALS_DIRECTORY/db_user"); DB_NAME=$$(cat "$$CREDENTIALS_DIRECTORY/db_name"); PROD_HOST=$$(cat "$$CREDENTIALS_DIRECTORY/prod_host"); PROD_KEY="$$CREDENTIALS_DIRECTORY/prod_key"; export DB_USER DB_NAME PROD_HOST PROD_KEY; exec /bin/bash $PROJECT_PATH/infra/homelab/backup/script/backup-homelab.sh'
```

Le script place son fichier de verrou dans `TMPDIR`. Ce répertoire privé évite
un conflit de permissions avec un verrou créé dans `/tmp` par un autre compte,
sans désactiver les protections système. Ne pas définir une autre valeur de
`TMPDIR` dans `backup.env`, qui prendrait priorité sur `Environment`.


Systemd fournit `CREDENTIALS_DIRECTORY` uniquement aux processus du service :
ne pas tester la lecture des credentials avec `sh test.sh` dans un shell
ordinaire. Le script actuel attend ces valeurs dans son environnement et
utilise la clé via un chemin ; les valeurs ne sont donc pas exclusivement
confinées aux fichiers de credentials. Le script peut aussi journaliser le
nom de la base ou l'hôte et transmettre des valeurs à SSH et aux commandes
distantes. Protéger les journaux et limiter l'accès au compte.

### 5. Vérification et planification

L'exemple ci-dessus lance une sauvegarde réelle. Pour commencer par une
simulation, ajouter `--dry-run` à la fin de la commande du script dans
`ExecStart` avant de recharger le service.

Dans une session du compte disposant de l'accès à son gestionnaire systemd
utilisateur, après avoir chargé la clé dans l'agent :

```bash
systemctl --user daemon-reload
systemctl --user start cron_job.service
systemctl --user status cron_job.service --no-pager
```

Le mode `--dry-run` teste notamment la connexion et les
statistiques distantes, mais ne valide pas une sauvegarde réelle. Il peut
créer des répertoires locaux et des fichiers temporaires. Vérifier le résultat
sans publier de journaux sensibles. Après validation et avant une sauvegarde
automatique réelle, retirer `--dry-run` de `ExecStart` puis recharger le
service avec `systemctl --user daemon-reload`.

Pour planifier une exécution quotidienne, créer
`~/.config/systemd/user/cron_job.timer` :

```ini
[Unit]
Description=Planification de la sauvegarde AmbianceBoard

[Timer]
OnCalendar=*-*-* 02:30:00
Persistent=true
Unit=cron_job.service

[Install]
WantedBy=timers.target
```

Activer le timer seulement lorsque la configuration et le comportement de la
sauvegarde ont été validés. `Persistent=true` peut déclencher une exécution
manquée au démarrage :

```bash
systemctl --user daemon-reload
systemctl --user enable --now cron_job.timer
systemctl --user list-timers --all --no-pager
```