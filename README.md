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

## 🤝 Avancement 
Suivi du projet
[clickUp](https://sharing.clickup.com/9014791178/l/h/8cn5k0a-554/d11e2ded9d8d1d4)

## Demarrage rapide

Le projet se lance principalement avec Docker Compose.

```sh
make init
make build
make up
make enter S=back
python manage.py createsuperuser
```

URLs locales les plus visibles dans l etat actuel du depot:

- Application: http://localhost:9999/
- RabbitMQ: http://localhost:15672/
- MailHog: http://localhost:8025/
- Grafana: http://localhost:3000/

Pour les details techniques, voir `ARCHITECTURE.md`, `TESTS.md`, `DEPLOY-PROD.MD`, `SECURITE.md` et `SECURITY.md`.

## Cas d usage couverts

- Construire une soundboard privee ou publique.
- Jouer musiques, effets et ambiances pendant une session TTRPG.
- Synchroniser une session partagee via WebSocket.
- Moderer ou administrer du contenu depuis des espaces dedies.

## Documentation Audit

- Date d audit: 2026-06-10
- Score: 58/100
- Statut: PARTIEL

### Constat

| Fichier | Etat | Probleme | Impact |
|---|---|---|---|
| README.md | updated | L ancien contenu etait utile pour un premier lancement, mais restait incomplet sur la valeur produit, le vrai demarrage rapide et l etat global de la documentation. | Moyen |
| ARCHITECTURE.md | updated | Le document existant couvrait une partie de l architecture mais melangeait audit, organisation cible et recommandations trop directes. | Eleve |
| DEPLOY-PROD.MD | observe | Le guide de deploiement existe mais reste procedural, peu structure et difficile a relier aux composants reels de l architecture. | Eleve |
| SECURITY.md / SECURITE.md | observe | Deux documents de securite coexistent avec des finalites differentes, ce qui cree une ambiguite sur la source de reference. | Moyen |
| TESTS.md | observe | Le document apporte un audit utile, mais reste separe du parcours principal de lecture de la documentation. | Moyen |

### Risques

- Onboarding plus lent pour un nouveau contributeur, car la documentation est dispersee entre plusieurs fichiers heterogenes.
- Mauvaise interpretation des commandes de demarrage si le lecteur suit un guide partiel ou ancien.
- Comprehension incomplete des frontieres entre produit, architecture, exploitation et securite.
- Dette documentaire croissante si les guides satellites evoluent sans point d entree unique.

### Pistes d amelioration

1. Stabiliser un parcours de lecture unique entre presentation produit, architecture, tests, deploiement et securite.
2. Uniformiser le niveau de detail et le format d audit des documents majeurs du depot.
3. Rendre explicites les prerequis d environnement et les variantes dev/prod sans surcharger le README.
4. Clarifier quelle documentation fait foi pour la securite, le deploiement et les tests.
5. Ajouter des vues synthetiques sur les flux critiques: lecture audio, synchro partagee, upload et traitement asynchrone.

### Etat du fichier

| Fichier | Statut | Resume changements |
|---|---|---|
| README.md | updated | Recentrage sur l objectif produit, le demarrage rapide reel et un audit synthetique de la documentation actuelle. |


