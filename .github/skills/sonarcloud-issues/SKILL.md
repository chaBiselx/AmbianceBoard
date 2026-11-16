---
name: sonarcloud-issues
description: "Consulter le projet SonarCloud AmbianceBoard, suivre l'évolution des issues ouvertes et prioriser leur réduction. À utiliser pour un point SonarCloud, une comparaison dans le temps ou un plan de correction."
argument-hint: "Point actuel, évolution depuis la dernière mesure ou priorisation des corrections"
---

# Suivi des issues SonarCloud

## Projet

- Projet : `chaBiselx_AmbianceBoard`
- URL : https://sonarcloud.io/project/overview?id=chaBiselx_AmbianceBoard
- Les endpoints REST du projet sont publics au moment de la rédaction. Cela ne constitue pas un accès MCP.

## Procédure

1. Avant toute modification, lire [AGENTS.md](../../../AGENTS.md) et les éventuelles instructions applicables aux fichiers concernés. Elles priment sur les raccourcis suggérés par une issue SonarCloud ; suivre aussi les conventions locales, les tests et les garde-fous du dépôt.
2. Récupérer les données à jour depuis l'API REST SonarCloud avec un outil HTTP disponible. Pour ce projet, commencer sans authentification :
   - Issues ouvertes : `https://sonarcloud.io/api/issues/search?componentKeys=chaBiselx_AmbianceBoard&resolved=false&ps=500&p=1`
   - Mesures : `https://sonarcloud.io/api/measures/component?component=chaBiselx_AmbianceBoard&metricKeys=bugs,vulnerabilities,code_smells,coverage,ncloc`
   - Quality Gate : `https://sonarcloud.io/api/qualitygates/project_status?projectKey=chaBiselx_AmbianceBoard`
3. Lire toutes les pages d'issues jusqu'à obtenir le nombre indiqué dans `paging.total`. Ne pas considérer la première page comme la liste complète.
4. Présenter la date de collecte, le total des issues non résolues, leur répartition par type (`BUG`, `VULNERABILITY`, `CODE_SMELL`) et sévérité (`BLOCKER`, `CRITICAL`, `MAJOR`, `MINOR`, `INFO`), l'effort estimé, et l'état du Quality Gate. Distinguer les mesures du projet des issues détaillées : les totaux ou catégories peuvent ne pas correspondre exactement.
5. Prioriser la sélection des corrections à partir des données observées : vulnérabilités et bugs d'abord, puis sévérité, impact, effort estimé et possibilités de traiter plusieurs occurrences ensemble. Donner les issues concernées (clé, fichier/ligne, règle, résumé) et proposer un petit lot de corrections actionnable.
6. Pour le lot demandé, ordonner la réalisation des issues de la plus simple à la plus complexe, selon l'effort et l'étendue du changement (fichiers concernés, contrats et dépendances). Conserver la priorité par risque pour sélectionner les issues ; à complexité comparable, traiter d'abord la plus prioritaire. Corriger la cause dans la couche responsable, avec un changement ciblé qui respecte les conventions et contrats du projet. Réutiliser les utilitaires et motifs existants (DRY) ; appliquer SRP et SOLID de façon pragmatique, sans abstractions spéculatives ni refactorisation hors sujet. Ajouter un test de régression proportionné au risque.
7. Respecter les responsabilités de couche définies dans `AGENTS.md` : un contrôleur traite la requête, valide l'entrée, applique l'autorisation et construit la réponse HTTP ; les règles métier et l'orchestration du cas d'usage appartiennent aux services ; l'accès aux données appartient aux repositories. Avant de déplacer ou d'extraire du code, inspecter les services, helpers et tests voisins pour réutiliser les motifs existants.
   - Pour réduire la complexité Sonar, une fonction auxiliaire peut être créée, mais jamais dans le même fichier que la vue/contrôleur concerné. La placer dans un module distinct dont la responsabilité correspond au code extrait : service pour les règles métier ou l'orchestration, helper cohérent pour une logique partagée. Ne pas créer un module artificiel uniquement pour déplacer quelques lignes.
   - Garder dans le contrôleur le traitement HTTP : parsing et validation de la requête, dispatch des actions HTTP et construction des réponses. Ne pas déplacer ces responsabilités dans un service ; si elles justifient une extraction, utiliser un module distinct approprié et préserver une vue comme adaptateur HTTP mince. Les règles métier et l'orchestration restent dans un service cohérent, existant ou nouveau.
   - Ne pas créer un service artificiel pour du simple parsing HTTP, de la validation de requête ou la construction d'une réponse ; cela reste dans le contrôleur. Choisir la frontière selon la responsabilité réelle, sans service « fourre-tout » ni découpage par méthode.
   - Préserver les contrats, permissions, quotas, transactions, traductions et comportements existants. Ajouter ou adapter des tests unitaires du service et, si la route ou son contrat est affecté, des tests d'intégration de la vue.
8. Pendant la réalisation, traiter uniquement les issues SonarCloud explicitement retenues : ignorer les TODO existants rencontrés dans le code ou les notes et ne pas élargir le lot pour les réaliser. Ne pas ajouter de TODO sans nécessité directement liée au correctif.
9. Lancer les validations prescrites par `AGENTS.md` depuis la racine et dans les conteneurs du projet : tests unitaires du service concerné (`make test-backend-tu`, `make test-frontend-tu` ou `make test-music-labeler-tu`), avec un `FILTER` ciblé si possible ; lancer aussi les tests d'intégration prescrits si les routes, la persistance ou plusieurs modules interagissent. Indiquer les commandes exécutées, leurs résultats et les validations non réalisées ou bloquées. Préciser qu'une nouvelle analyse SonarCloud sera nécessaire pour confirmer la baisse.

## Fiabilité et accès

- Les résultats peuvent changer après une nouvelle analyse SonarCloud. Toujours refaire la requête ; dater les chiffres et ne pas extrapoler à partir d'une ancienne mesure.
- Conserver l'historique hors du dépôt ; ne pas créer ou modifier de fichier d'historique sous `reports/` ou un autre chemin du projet.
- Si l'accès public échoue ou si l'API demande une authentification, indiquer clairement le blocage. Ne jamais demander ni afficher de jeton dans le chat ; utiliser uniquement un mécanisme de secret configuré hors du dépôt si l'utilisateur en met un en place.
- Ne pas présenter un appel REST, une lecture de page web ou ce skill comme un serveur MCP.
