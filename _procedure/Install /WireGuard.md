# VPN WireGuard entre un VPS et un serveur maison

WireGuard est le choix le plus simple et le plus léger pour relier un VPS et un serveur à la maison. Le VPS a une IP publique, il sert donc de point fixe : c'est le serveur maison qui initie la connexion. Il n'y a **aucune redirection de port à faire sur la box**.

## Plan d'adressage

| Machine        | Adresse VPN   |
|----------------|---------------|
| Réseau VPN     | `10.10.10.0/24` |
| VPS            | `10.10.10.1`  |
| Serveur maison | `10.10.10.2`  |

## 1. Installation (sur les deux machines)

```bash
sudo apt update && sudo apt install wireguard
```

## 2. Génération des clés (sur les deux machines)

```bash
umask 077
wg genkey | tee privatekey | wg pubkey > publickey
```

Garder la clé privée sur chaque machine et échanger uniquement les clés publiques.

## 3. Configuration du VPS

Le playbook Ansible crée `/etc/wireguard/wg0.conf` s'il n'existe pas, avec l'adresse `10.10.10.1/24`, le port `51820` et la clé publique du serveur maison fournie dans `WIREGUARD_LOCAL_PUBLIC_KEY`. Il faut définir cette variable avant d'exécuter le playbook.

Le contenu attendu est :

```ini
[Interface]
Address = 10.10.10.1/24
ListenPort = 51820
PrivateKey = <CLÉ_PRIVÉE_DU_VPS>

[Peer]
# Serveur maison
PublicKey = <CLÉ_PUBLIQUE_MAISON>
AllowedIPs = 10.10.10.2/24
```

Ouvrir le port UDP sur le VPS :

```bash
sudo ufw allow 51820/udp
```

## 4. Configuration du serveur maison

Fichier `/etc/wireguard/wg0.conf` :

```ini
[Interface]
Address = 10.10.10.2/24
PrivateKey = <CLÉ_PRIVÉE_MAISON>

[Peer]
# VPS
PublicKey = <CLÉ_PUBLIQUE_DU_VPS>
Endpoint = <IP_PUBLIQUE_DU_VPS>:51820
AllowedIPs = 10.10.10.1/24
PersistentKeepalive = 25
```

> `PersistentKeepalive` est indispensable ici : il maintient le tunnel ouvert à travers le NAT de la box.

## 5. Démarrage

Activer le port dans le par feu de l'herbergeur 

Le playbook Ansible active et démarre automatiquement `wg-quick@wg0` sur le VPS. Sur chaque machine configurée manuellement, exécuter :

```bash
sudo systemctl enable --now wg-quick@wg0
```

## 6. Test

```bash
sudo wg show          # doit afficher un "latest handshake"
ping 10.10.10.1       # depuis la maison
ping 10.10.10.2       # depuis le VPS
```

## 7. Utilisation pour l'administration

On peut maintenant se connecter en SSH via le tunnel :

- `ssh user@10.10.10.1` depuis la maison
- `ssh user@10.10.10.2` depuis le VPS

### Sécuriser SSH sur le VPS (optionnel)

Restreindre SSH au VPN uniquement. **À faire seulement après avoir vérifié que le tunnel fonctionne**, sinon il y a un risque de se verrouiller dehors :

```bash
sudo ufw allow in on wg0 to any port 22
sudo ufw delete allow 22/tcp    # ou 'OpenSSH' selon la règle actuelle
```

Garder une session SSH ouverte pendant le test, ou une console de secours chez l'hébergeur.

### paramètrer SSH 

rentré dans `sudo vi /etc/ssh/sshd_config`

```
# Utilisateur docker stats : autorisé uniquement depuis 10.10.10.2
Match User user_docker_stat Address 10.10.10.2
    PubkeyAuthentication yes
    PasswordAuthentication no
    KbdInteractiveAuthentication no
    AllowTcpForwarding no
    X11Forwarding no
    AllowAgentForwarding no
    PermitTunnel no
    PermitTTY no

# Toute autre origine pour ce même utilisateur : refusé
Match User user_docker_stat Address *,!10.10.10.2
    DenyUsers user_docker_stat
```

```
sudo sshd -t   
sudo systemctl restart ssh  
```

verifier la connexion avec : 
```
ssh -i ~/.ssh/id_ed25519_ambianceboard_docker_stat user_docker_stat@10.10.10.1 "hostname && docker ps"
```



Dans ~/.ssh/config de l’utilisateur qui lancera Docker :
```
Host 10.10.10.1
    User user_docker_stat
    IdentityFile ~/.ssh/id_ed25519_ambianceboard_docker_stat
    IdentitiesOnly yes
```

puis `chmod 600 ~/.ssh/config`

```bash
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519_ambianceboard_docker_stat
```

créer le distant docker : 
```
docker context create distant --docker "host=ssh://user_docker_stat@10.10.10.1"
```

## Extensions possibles

- **Accéder à tout le LAN maison depuis le VPS** : ajouter le sous-réseau (ex. `192.168.1.0/24`) dans `AllowedIPs` du peer côté VPS, activer `net.ipv4.ip_forward=1` sur le serveur maison et configurer le NAT/forward.
- **Ajouter un PC ou un téléphone** : ajouter un nouveau `[Peer]` côté VPS avec une IP `10.10.10.3/32`, etc.


