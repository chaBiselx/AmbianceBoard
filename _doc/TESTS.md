# Tests via Makefile

## Prerequis et execution

Executer les commandes depuis la racine du depot. Le
[Makefile](../Makefile) inclut [Test.mk](../makeFileFolder/Test.mk) et lance les
outils de test dans les conteneurs Docker Compose, pas sur l'hote.
Docker Compose doit etre disponible et les services necessaires demarres :
`back` pour Django, `front` pour Vitest et `music-labeler` pour pytest.
Les integrations peuvent egalement necessiter la base, Redis ou d'autres
services : verifier le test concerne et sa configuration.

`make help` liste les cibles ; `make -n <cible>` affiche leur recette sans
l'executer. La simulation ne valide ni les dependances ni les tests.
Ne pas lancer automatiquement `make init`, `make up` ou `make db-reset`
pour preparer une validation : voir les precautions ci-dessous.

## Cibles disponibles

| Commande | Perimetre |
| --- | --- |
| `make test-backend-tu` | Django, tag `unitaire` |
| `make test-backend-ti` | Django, tag `integration` |
| `make test-backend-st` | Django, tag `stress-test` |
| `make test-backend` | TU + TI + stress backend |
| `make test-stress` | Alias des tests de stress backend |
| `make test-frontend-tu` | Vitest, `tests/TU` |
| `make test-frontend-ti` | Vitest, `tests/TI` |
| `make test-frontend` | TU + TI frontend |
| `make test-music-labeler-tu` | pytest, `tests` |
| `make test-music-labeler` | Actuellement alias de la suite TU labeler |
| `make test-e2e` | Preparation backend et Playwright dans le profil `test` |
| `make test-all` | Backend (dont stress), frontend, labeler et E2E |

Les tests sont dans [app/main/TNR](../app/main/TNR/),
[frontend/tests](../frontend/tests/) et [music-labeler/tests](../music-labeler/tests/).
La decouverte Django s'appuie notamment sur [main/tests.py](../app/main/tests.py).
`make test-frontend` ne lance pas le script npm `test` : il ne comprend donc
pas automatiquement le test smoke distinct declare dans
[package.json](../frontend/package.json).

## Cibler les tests avec FILTER

Utiliser `FILTER`, pas `TEST`. Les cibles filtrees ne partagent pas le meme sens :

- Backend TU/TI/stress : label Django (module, classe ou methode), en conservant
  le tag de la cible. Exemple de perimetre :
  `make test-backend-tu FILTER=main.TNR.TU`.
- Frontend TU/TI : expression de nom de test transmise a Vitest par
  `--testNamePattern`, pas un chemin de fichier. Choisir un nom de `describe`
  ou de test existant : `make test-frontend-tu FILTER=Onboarding`.
- Labeler TU : chemin ou identifiant pytest relatif au conteneur, remplace
  le repertoire `tests` : `make test-music-labeler-tu FILTER=tests`.

Confirmer qu'au moins un test attendu a ete execute : un filtre sans
correspondance ne constitue pas une verification du comportement.
`FILTER` n'est pas exploite par les recettes de couverture ou E2E actuelles.

## Couverture

| Commande | Controle actuel |
| --- | --- |
| `make test-backend-coverage` | coverage.py, exclut `stress-test`, minimum 60 % |
| `make test-frontend-coverage` | Vitest avec couverture, seuils dans `vite.config.ts` |
| `make test-music-labeler-coverage` | pytest-cov, minimum 60 % |
| `make test-all-coverage` | Execute les trois controles puis affiche leur moyenne |

La moyenne affichee est une moyenne arithmetique des pourcentages de service,
pas une couverture ponderee par le nombre total de lignes. Elle ne remplace
pas les seuils propres a chaque service et n'inclut pas les E2E.
Ne pas baisser les seuils pour faire passer une modification.

## Precautions sur l'environnement

- `make test-e2e` lance des migrations et commandes de fixtures avec une
  surcharge SQLite, demarre `back`, puis lance le conteneur Playwright.
  Utiliser un environnement dedie ; verifier la configuration effective du
  backend et la persistance de la base entre preparation et execution.
  La commande de demarrage de `back` n'explicite pas les memes surcharges
  `-e` que la commande de preparation.
- `make test-all` inclut ces effets E2E et les tests de stress : ce n'est pas
  la verification par defaut d'un correctif local.
- Dans [Gestion.mk](../makeFileFolder/Gestion.mk), `make up` depend de
  `clear-old-containers`, qui execute des purges Docker globales, et suit les
  logs. `make restart` passe aussi par cette cible. Demander un accord avant
  leur execution ; ne pas les utiliser pour un simple lancement de tests.
- Les recettes `init`/`init-prod` referencent `.env.dev.sample` et
  `.env.prod.sample`, alors que les exemples presents utilisent `-sample`.
  Ne pas supposer ces cibles operationnelles pour un premier demarrage.
- `make db-reset` est une remise a zero, pas un prerequis anodin de test.

## Choix de validation

Commencer par le test le plus proche du comportement modifie, puis executer
les suites des contrats touches. Pour les routes, droits ou migrations,
completer par les TI backend. Pour les interactions entre modules, utiliser
les TI frontend ; pour un parcours utilisateur transverse, prevoir les E2E
dans un environnement dedie. Pour la documentation seule, verifier les liens
et simuler les cibles Make citees.

Dans le compte rendu, distinguer tests reussis, simulations et controles non
executes, avec la raison des blocages. Ne pas annoncer une couverture mesuree
sans avoir execute la cible correspondante.