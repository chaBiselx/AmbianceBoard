# Utiliser OWASP ZAP dans un Docker Compose

> Export de la conversation. Projet de référence : [AmbianceBoard – docker-compose.yml](https://github.com/chaBiselx/AmbianceBoard/blob/master/docker-compose.yml)

## Question

Comment utiliser ZAP dans un Docker Compose sur un projet comme celui d'AmbianceBoard ?

## Remarque préalable

Le fichier `docker-compose.yml` du dépôt n'a pas pu être lu (accès GitHub bloqué). Les exemples ci-dessous partent donc d'une stack web classique (une application, une base de données, éventuellement nginx). Les noms de services et les ports sont à adapter.

## Principe

ZAP doit être sur le **même réseau Docker** que l'application. Il la cible alors par son **nom de service** (`http://web:8000`) et non par `localhost`. Le plus propre est de l'ajouter dans un **profil** Compose pour qu'il ne se lance pas avec un `docker compose up` habituel.

## Service ZAP à ajouter

```yaml
services:
  # ... vos services existants (web, db, nginx, redis...) ...

  zap:
    image: ghcr.io/zaproxy/zaproxy:stable
    profiles: ["security"]          # ne démarre que sur demande
    depends_on:
      web:
        condition: service_started  # idéalement service_healthy (voir plus bas)
    volumes:
      - ./zap-reports:/zap/wrk:rw   # rapports écrits ici
    user: root                      # évite les soucis de droits sur /zap/wrk
    networks:
      - default                     # même réseau que l'app (adapter au nom du réseau)
    command: >
      zap-baseline.py
      -t http://web:8000
      -r rapport-baseline.html
      -J rapport-baseline.json
      -I
```

- Remplacer `web:8000` par le service et le port **internes** du conteneur qui sert l'application (pas le port publié sur l'hôte).
- Si nginx est placé devant, cibler nginx (`http://nginx:80`) pour tester ce que voit réellement un utilisateur.

## Lancement

```bash
mkdir -p zap-reports
docker compose up -d                       # stack normale
docker compose --profile security run --rm zap
```

Le rapport apparaît dans `./zap-reports/`.

## Les trois types de scan

| Script | Usage | Durée |
|---|---|---|
| `zap-baseline.py` | Scan **passif** (spider court, aucune attaque) | quelques minutes |
| `zap-full-scan.py` | Spider + scan **actif** (attaques réelles) | long |
| `zap-api-scan.py` | À partir d'une spec OpenAPI/Swagger | variable |

L'option `-I` évite que le scan retourne une erreur lorsqu'il trouve des alertes. Il faut la retirer en CI pour faire échouer le pipeline.

> ⚠️ **Scan actif** : il envoie de vraies requêtes d'attaque (injections, etc.). À lancer uniquement sur un environnement de dev ou de test, jamais en production, et avec une base de données jetable.

## Pièges fréquents

### 1. L'application n'est pas prête au lancement de ZAP

Ajouter un healthcheck sur `web`, puis utiliser `condition: service_healthy` :

```yaml
  web:
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/"]
      interval: 5s
      timeout: 3s
      retries: 20
```

### 2. Host refusé (Django, Symfony, etc.)

Si le framework valide le header `Host`, le nom de service Docker (`web`, `nginx`) sera rejeté. Pour Django, l'ajouter à `ALLOWED_HOSTS` en environnement de test.

### 3. Erreur de droits sur `/zap/wrk`

L'utilisateur interne `zap` est en UID 1000. Soit garder `user: root`, soit faire `chmod 777 zap-reports`.

### 4. Redirections HTTPS

Si l'application force le HTTPS, le scan en HTTP sera redirigé. Désactiver la redirection en environnement de test, ou cibler directement le port HTTPS.

## Scan d'une zone authentifiée

Le scan baseline ne voit que les pages publiques. Deux approches pour scanner derrière un login :

- utiliser un **fichier de contexte / Automation Framework** (`zap.sh -cmd -autorun plan.yaml`) avec une authentification par formulaire ;
- passer un token ou un cookie de session via un header, par exemple :

```bash
-z "-config replacer.full_list(0).description=auth \
    -config replacer.full_list(0).enabled=true \
    -config replacer.full_list(0).matchtype=REQ_HEADER \
    -config replacer.full_list(0).matchstring=Authorization \
    -config replacer.full_list(0).replacement='Bearer VOTRE_TOKEN'"
```

## Variante : ZAP en daemon avec interface

Pour piloter ZAP manuellement via l'interface web :

```yaml
  zap:
    image: ghcr.io/zaproxy/zaproxy:stable
    profiles: ["security"]
    command: zap-webswing.sh
    ports:
      - "8080:8080"   # interface
      - "8090:8090"   # webswing
```

Ouvrir ensuite `http://localhost:8080/zap/` et utiliser `http://web:8000` comme cible.

## En CI (GitHub Actions)

Il est aussi possible de ne pas passer par le compose pour ZAP et d'utiliser l'action officielle `zaproxy/action-baseline` après avoir lancé la stack. Le principe reste le même : même réseau, cible par nom de service ou par `localhost:port` selon l'endroit où tourne ZAP.

## Suite possible

En fournissant le contenu du `docker-compose.yml` d'AmbianceBoard, le service ZAP pourra être écrit avec les noms exacts de réseau, de services et de ports.
