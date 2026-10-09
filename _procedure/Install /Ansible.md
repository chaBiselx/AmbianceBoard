# Installation d'Ansible

## Structure du projet

```text
ansible/
├── ansible.cfg
├── group_vars
│   └── all.yml
├── inventory/
│   └── prd
│       ├── hosts.ini
│       └── group_vars
│           └── all.yml
├── playbooks/
│   └── setup.yml
└── roles/
    ├── common/
    ├── nginx/
    └── docker/
```

Rôle des principaux éléments :

- `ansible.cfg` : configuration générale d'Ansible (SSH, utilisateur, journaux, etc.).
- `inventory` : inventaire des environnements.
- `playbooks` : actions à exécuter avec Ansible.
- `group_vars` : variables des machines.
- `group_vars/all.yml` : variables communes à toutes les machines.
- `inventory/prd/group_vars/all.yml` : variables communes aux machine de prd.
- `roles` : tâches réutilisables.

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
ansible-playbook -i ./ansible/inventory/prd/hosts.yml ./ansible/playbooks/setup.yml
```

