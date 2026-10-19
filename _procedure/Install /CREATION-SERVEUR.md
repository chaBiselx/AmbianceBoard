

# Installation d’Ubuntu Server

## Prérequis

- Préparer une clé USB ou un disque dur contenant le programme d’installation.
- Connecter le serveur au réseau local (LAN) dès le début de l’installation.

## Installation

1. Brancher le support d’installation et démarrer la machine en appuyant plusieurs
   fois sur `F7` ou `Échap`.
2. Choisir **Try or Install Ubuntu Server**.
3. Choisir la version standard si une personne doit facilement accéder au serveur ;
   sinon, choisir la version minimale (*minimized*).

Si la version minimale est déjà installée, la commande `sudo unminimize` rétablit
une grande partie des paquets et de la documentation retirés.

Terminer l’installation en écrasant le disque de la machine.

Activer **OpenSSH** pendant l’installation.

Pour modifier la date après l’installation :

```bash
sudo date -s '2026-12-01 20:00:00'
```

## Après l’installation

### Supprimer une autre entrée de démarrage

Afficher les entrées de démarrage :

```bash
sudo efibootmgr
```

Pour supprimer une entrée, remplacer `id_boot` par son identifiant. Par exemple,
pour l’entrée `Boot0002`, utiliser `0002` :

```bash
efibootmgr -b id_boot -B
```

passer à l'installation d'Ansible