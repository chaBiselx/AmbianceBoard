# Guide de travail des agents - AmbianceBoard

## Contexte et references

AmbianceBoard est une application de soundboards pour jeux de role : preparation
audio, partage public/prive, sessions temps reel et labellisation des pistes.
Le depot regroupe un backend Django, un frontend TypeScript/Vite et un service
Python FastAPI de labellisation audio, executes avec Docker Compose.

- [Architecture et analyse du projet](_doc/ARCHITECTURE.md).
- [Tests, commandes Make et precautions](_doc/TESTS.md).
- [Presentation du produit](README.md) et [historique](TAGS.md).
- [Politique de securite](SECURITY.md).

## Methode de travail

- Lire les instructions applicables et le code voisin avant de modifier.
- Identifier le comportement concerne, sa couche proprietaire et un test cible.
- Faire le plus petit changement coherent ; ne pas refactoriser des modules
  sans rapport avec la demande ni ecraser les modifications existantes.
- Respecter les conventions locales de nommage, d'import, de traduction et de
  tests. Reutiliser les utilitaires et les fichiers de tests existants.
- Mettre a jour la documentation si une responsabilite, un flux ou une commande
  change. Ne pas presenter une architecture souhaitee comme deja implementee.

## Responsabilites et SRP

Appliquer le principe de responsabilite unique (SRP) de maniere generale : une
fonction, une classe ou un module doit avoir une responsabilite coherente et
une raison principale de changer. SRP ne signifie pas une classe par methode.

- Controleurs : requete, validation d'entree, autorisation et reponse HTTP.
- Services : regles metier et orchestration du cas d'usage.
- Repositories : acces aux donnees et requetes de persistance.
- Frontend : distinguer autant que possible interactions DOM, etat de lecture,
  moteur audio et communication reseau.
- Labeler : distinguer API HTTP, traitement audio et inference du modele.

Ne pas ajouter de requetes ORM aux templates ou de logique metier aux handlers
DOM. Quand plusieurs raisons de changer apparaissent, extraire une
responsabilite a la frontiere existante la plus proche, avec des tests.

## SOLID pragmatique

Appliquer SOLID lorsqu'il simplifie naturellement la modification, sans
introduire d'abstractions speculatives ou imposer une migration globale.

- **S - SRP** : suivre les responsabilites ci-dessus.
- **O - Ouvert/ferme** : etendre une strategie ou un adaptateur existant quand
  une nouvelle variante le justifie, plutot que multiplier les conditions.
- **L - Substitution** : les implementations doivent respecter les contrats,
  erreurs et effets attendus ; tester le comportement commun.
- **I - Segregation des interfaces** : preferer des contrats courts, limites
  aux besoins reels du consommateur, aux interfaces universelles.
- **D - Inversion des dependances** : reutiliser les contrats disponibles.
  Injecter une dependance externe lorsqu'elle facilite concretement les tests
  ou un remplacement. Ne pas ajouter de conteneur DI ou d'interface pour
  chaque repository uniquement pour satisfaire un principe.

Le domaine actuel depend encore de Django et de repositories concrets :
preserver les contrats existants et ameliorer localement, sans pretendre que
le projet est une architecture hexagonale pure.

## Validation obligatoire

Executer les tests via le [Makefile](Makefile), depuis la racine du depot,
dans les conteneurs du projet. Ne pas utiliser l'environnement Python/Node
de l'hote pour les tests applicatifs.

- Backend : `make test-backend-tu`, puis `make test-backend-ti` si la
  persistance, les routes ou un contrat d'integration changent.
- Frontend : `make test-frontend-tu`, puis `make test-frontend-ti` si plusieurs
  modules interagissent.
- Labeler : `make test-music-labeler-tu`.
- Commencer par un `FILTER` cible lorsque possible ; sa signification depend
  du service, voir [le guide des tests](_doc/TESTS.md).
- Ajouter un test de regression pour un correctif, proportionne au risque.
- Relancer le test cible immediatement apres le changement, puis les suites
  necessaires aux contrats affectes. Ne pas lancer automatiquement les tests
  de stress ou E2E pour une modification locale.
- Pour la couverture : `make test-backend-coverage`,
  `make test-frontend-coverage`, `make test-music-labeler-coverage` ;
  `make test-all-coverage` regroupe ces controles.
- Pour la documentation seule : verifier liens, chemins et commandes
  (`make -n <cible>`), sans executer les suites applicatives inutilement.

Indiquer les commandes executees, leur resultat et toute validation bloquee
ou non realisee. Une execution a blanc n'est pas un test applicatif reussi.

## Garde-fous

- Ne pas lire, afficher ou versionner les secrets des fichiers `.env`, les
  tokens, les donnees utilisateurs ni les journaux contenant ces donnees.
- Ne pas lancer de deploiement, purge Docker ou remise a zero de base sans
  accord explicite. `make up` depend actuellement de `clear-old-containers` ;
  `make db-reset` reinitialise la base. Les E2E modifient l'environnement.
- Ne pas modifier les sorties generees (`staticfiles`, bundles, couverture,
  resultats E2E), les medias ou les donnees de base pour corriger le code source.
- Preserver les autorisations, quotas, transactions, traductions FR/EN et les
  contrats WebSocket lors des evolutions fonctionnelles.
- Ne pas committer ou pousser sans demande explicite.