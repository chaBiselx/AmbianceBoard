# AmbianceBoard

AmbianceBoard est une application web de soundboard pour jeux de role sur table.
Elle permet de preparer des ambiances sonores, d organiser des playlists et de partager des sessions de lecture pour soutenir une partie sans multiplier les outils.

## A qui sert le produit

- Meneurs de jeu qui veulent piloter musiques, boucles d ambiance et effets ponctuels depuis une meme interface.
- Groupes qui veulent partager une soundboard publiquement ou via un espace prive.
- Equipes qui exploitent un produit web Dockerise avec backend Django, frontend TypeScript et fonctions temps reel.

## 📊 SonarCloud  
![Quality Gate](https://sonarcloud.io/api/project_badges/measure?project=chaBiselx_AmbianceBoard&metric=alert_status) 
![Security](https://sonarcloud.io/api/project_badges/measure?project=chaBiselx_AmbianceBoard&metric=security_rating)
![Reliability](https://sonarcloud.io/api/project_badges/measure?project=chaBiselx_AmbianceBoard&metric=reliability_rating) 
![Maintainability](https://sonarcloud.io/api/project_badges/measure?project=chaBiselx_AmbianceBoard&metric=sqale_rating) 
![Duplication](https://sonarcloud.io/api/project_badges/measure?project=chaBiselx_AmbianceBoard&metric=duplicated_lines_density)  
👉 [Voir le rapport SonarCloud](https://sonarcloud.io/project/overview?id=chaBiselx_AmbianceBoard)  

## 📊 Score  
[![Plumber Score](https://score.getplumber.io/github.com/chabiselx/ambianceboard.svg)](https://score.getplumber.io/github.com/chabiselx/ambianceboard)

## 🤝 Avancement 
Suivi du projet
[clickUp](https://sharing.clickup.com/9014791178/l/h/8cn5k0a-554/d11e2ded9d8d1d4)

## Demarrage rapide

Le projet se lance principalement avec Docker Compose.

```sh
make init
make build
make up
make db-reset
```

l'identifiant / mot de passe pour le dev
root/root

URLs locales les plus visibles dans l etat actuel du depot:

ajouter dans le dns 127.0.0.1 ambianceboard

- Application: http://ambianceboard/
- RabbitMQ: http://localhost:15672/
- MailHog: http://localhost:8025/
- Grafana: http://localhost:3000/


