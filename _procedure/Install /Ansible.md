# Installation d'Ansible

## Structure du projet

```text
ansible/
├── ansible.cfg
├── group_vars/
│   └── all.yml
├── inventory/
│   └── prd/
│       ├── group_vars/
│       │   └── all.yml
│       └── host.yaml.j2
├── playbooks/
│   └── setup.yml
└── role/
    └── _template/
        ├── defaults/
        ├── handlers/
        ├── meta/
        ├── molecule/
        ├── task/
        ├── template/
        └── vars/
```

### Rôle des éléments

- `ansible.cfg` : configuration Ansible du dépôt, notamment l'inventaire par défaut, le délai d'attente et le contrôle de la clé SSH.
- `inventory/prd/host.yaml.j2` : modèle Jinja2 de l'inventaire de production. Il décrit le groupe `serveur_web`, l'hôte cible, l'utilisateur SSH et la clé privée. C'est un modèle, pas un inventaire final directement prêt à être utilisé.
- `inventory/prd/group_vars/all.yml` : variables propres à l'inventaire de production. L'adresse de l'hôte est lue dans `ANSIBLE_HOST_MAIN` et le port dans `ANSIBLE_SSH_PORT` (22 par défaut).
- `group_vars/all.yml` : variables communes à l'ensemble des hôtes, comme le port SSH par défaut.
- `playbooks/setup.yml` : playbook d'installation/configuration. Il met actuellement à jour le cache APT et les paquets du groupe `serveur_web`.
- `role/_template/` : gabarit prêt à copier pour créer un rôle réutilisable. Il contient les points d'entrée YAML, un exemple de template Jinja2 et un scénario Molecule Docker minimal. Les tâches et handlers sont vides pour éviter tout effet de bord avant l'implémentation du rôle.

### Structure d'un rôle

Cette organisation reprend la séparation courante des rôles Ansible

- `defaults/main.yaml` : valeurs par défaut configurables par l'utilisateur du rôle. Ansible leur donne une priorité faible afin qu'elles puissent être remplacées facilement.
- `handlers/main.yaml` : actions déclenchées uniquement lorsqu'une tâche les appelle avec `notify`, par exemple le redémarrage d'un service après un changement de configuration.
- `meta/main.yaml` : métadonnées du rôle et éventuelles dépendances envers d'autres rôles.
- `molecule/default/` : scénario Molecule Docker minimal. `molecule.yml` configure l'instance, `converge.yml` exécute le rôle et `verify.yml` vérifie que l'instance répond.
- `task/main.yml` : point d'entrée des tâches du rôle. Il peut inclure d'autres fichiers de tâches ; il est vide dans le gabarit.
- `template/example.yaml.j2` : exemple de fichier modèle Jinja2, utilisant une variable définie dans `defaults`.
- `vars/main.yaml` : variables internes au rôle, de priorité supérieure aux valeurs de `defaults`. À réserver aux valeurs qui ne sont pas destinées à être redéfinies par l'utilisateur du rôle.

Les noms `task/` et `template/` sont au singulier dans ce gabarit. Les rôles Ansible utilisent souvent `tasks/` et `templates/` au pluriel ; conserver une seule convention de nommage dans le dépôt et adapter les chemins des playbooks en conséquence.

> Le modèle d'inventaire `host.yaml.j2` n'est pas rendu automatiquement par les fichiers Ansible présents. Avant l'exécution, il faut produire un inventaire utilisable et faire correspondre son chemin à celui configuré dans `ansible.cfg` (`inventory/prd/host.ini` actuellement).

## Installation

### Sur le VPS

Utiliser un utilisateur dédié à Ansible.

```bash
sudo apt update && sudo apt install -y ansible
```

Vérifier l'installation :

```bash
ansible --version
```

### En local

```bash
sudo apt install -y ansible
```

## Utilisation

### Variables d'environnement

```bash
export ANSIBLE_SSH_PORT=22
export ANSIBLE_HOST_MAIN=X.X.X.X
```

### Préparation de l'agent SSH

```bash
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519_ambianceboard_ansible
```

### Exécution du playbook

```bash
cd ./ansible
ansible-playbook -i <chemin_vers_inventaire_genere> playbooks/setup.yml
```

Depuis la racine du dépôt, se placer dans `ansible/` permet à Ansible de charger `ansible.cfg`. Remplacer `<chemin_vers_inventaire_genere>` par le chemin de l'inventaire produit à partir de `inventory/prd/host.yaml.j2`. Le fichier doit être utilisable par Ansible ; sans option `-i`, Ansible utilisera le chemin déclaré dans `ansible.cfg` (`inventory/prd/host.ini`).

