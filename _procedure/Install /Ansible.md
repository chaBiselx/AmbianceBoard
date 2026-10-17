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

> L'inventaire `host.yaml.j2` est chargé directement par le plugin YAML grâce à `yaml_valid_extensions` dans `ansible.cfg`. Les expressions Jinja2 de ses variables sont évaluées lors de l'exécution ; aucun fichier `hosts.yml` n'est nécessaire.

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
export ANSIBLE_CONFIG=./ansible/ansible.cfg
```

### Préparation de l'agent SSH

```bash
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519_ambianceboard_ansible
```

### Exécution du playbook

```bash
cd ./ansible
ansible-playbook ./playbooks/setup.yml
```

Depuis la racine du dépôt, se placer dans `ansible/` permet à Ansible de charger `ansible.cfg`, qui configure `host.yaml.j2` comme inventaire YAML. Le suffixe `.j2` est ajouté aux extensions YAML prises en charge. Le rôle `common` est résolu depuis `roles/`.

Pour rester à la racine du dépôt, charger explicitement cette configuration :

```bash
ansible-playbook ./ansible/playbooks/setup.yml
```

Les chemins d'inventaire et de rôles sont relatifs à `ansible.cfg`. Sans `ANSIBLE_CONFIG`, Ansible ne recherche pas la configuration dans le sous-répertoire `ansible/`.

Vérifier la syntaxe sans connexion au serveur ni modification distante :

```bash
ansible-playbook --syntax-check ./ansible/playbooks/setup.yml
```

### Priorité variable

| Priorité | Emplacement (depuis la racine du dépôt) | Exemple / remarque |
|:--:|---|---|
| 1 (faible) | `roles/_template/defaults/main.yaml` | Valeurs par défaut, faites pour être écrasées. Après copie du gabarit, remplacer `_template` par le nom du rôle. |
| 2 | `inventory/prd/group_vars/all.yml` | Variables de tous les hôtes de l'inventaire de production. |
| 3 | `playbooks/group_vars/all.yml` | Variables communes, placées à côté du playbook. |
| 4 | `inventory/prd/group_vars/<groupe>.yml` | Variables du groupe d'inventaire, plus précises que `all`. |
| 5 | `playbooks/group_vars/<groupe>.yml` | Variables de groupe placées à côté du playbook. |
| 6 | `inventory/prd/host_vars/<hôte>.yml` | Variables de l'hôte, plus précises que celles du groupe. |
| 7 | `playbooks/host_vars/<hôte>.yml` | Variables d'hôte placées à côté du playbook. |
| 8 | Facts de l'hôte | `ansible_facts`, découverts à l'exécution |
| 9 | `vars:` dans `playbooks/setup.yml` | Variables définies dans le playbook |
| 10 | `vars_prompt:` dans `playbooks/setup.yml` | Saisie interactive |
| 11 | `vars_files:` dans `playbooks/setup.yml` | Fichiers référencés par le playbook |
| 12 | `roles/_template/vars/main.yaml` | Variables internes, difficiles à écraser. Après copie du gabarit, remplacer `_template` par le nom du rôle. |
| 13 | `vars:` d'un bloc, par exemple dans `roles/_template/tasks/main.yml` | `block:` |
| 14 | `vars:` d'une tâche, par exemple dans `roles/_template/tasks/main.yml` | Très local |
| 15 | `include_vars` dans une tâche, par exemple dans `roles/_template/tasks/main.yml` | Chargement pendant l'exécution |
| 16 | `set_fact` / `register` dans une tâche, par exemple dans `roles/_template/tasks/main.yml` | Variables définies pendant l'exécution |
| 17 | `vars:` sur un rôle dans `playbooks/setup.yml` | Paramètres transmis au rôle (`roles: - role: x` avec `vars:`) |
| 18 (fort) | `-e` / `--extra-vars` | Gagne toujours |
