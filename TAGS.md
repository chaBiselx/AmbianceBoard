

------------------------------
## Historique
### 0.1.0-beta.1 - 2025/09
Nouveautés
- Création de soundboards personnalisés (nom, couleurs, icône, public/privé)
- Organisation de plusieurs playlists par soundboard (ordre défini)
- Trois types de playlists : Ambiance continue, Effets instantanés, Musiques
- Upload de sons & musiques (ajout direct dans une playlist)
- Ajout de liens vers fichier en ligne
- Ajout de liens vers streaming (radio)
- Ajustement du volume global d’une playlist appliqué automatiquement aux sons
- Tags sur les soundboards + filtrage par tag dans l’interface
- Ajout de soundboards publics en favoris
- Mode plein écran pour se concentrer sur l’écoute / préparation
- Notifications d’information avec possibilité de masquer ce qui a été lu
- Signalement (report) d’un soundboard ou d’une playlist (interface guidée)
- Partage public d’un soundboard (lien accessible)
- Première version de session partagée en temps réel (mise à jour live précoce)
- Base des tiers utilisateurs (sans paiement)

### 0.1.0-beta.2 - 2025/09
Corrections
- Fix du script de déploiement


### 0.1.0-beta.3 - 2025/10
Nouveautés
- Ajout des préférences selon le type de support
- Ajout des sections pour les playlists pour l'organisation et la lecture des playlists

Améliorations
- Amélioration de l'esthétique des pages d'erreurs
- Amélioration du logger pour bêta-testeur

Fiabilité & Confiance
- Refactorisation pour utiliser des repositories au lieu des models

Corrections
- Correction de l'anomalie qui augmentait progressivement lorsque l'utilisateur souhaitait reporter du contenu

### 0.1.0-beta.4 - 2025/10
Nouveautés
- Possibilité de sélectionner des boutons qui peuvent être joués par les joueurs

Améliorations
- Amélioration du visuel pour organiser les boutons d'une playlist
- Ajout de tooltip sur les mixers
- Ajout d'une mise à jour des dates de connexion avec la variable de session

Corrections
- Fix du script de déploiement qui ne récupérait pas le dernier tag. 

### 0.1.0-beta.5 - 2025/10
Améliorations
- Amélioration du logger pour bêta-testeur
- Affichage du nom du soundboard

Nouveautés
- Ajout de Grafana pour la gestion des logs en production

### 0.1.0-beta.6 - 2025/10
Améliorations
- Connexion des logs à Loki pour Grafana

### 0.1.0-beta.7 - 2025/10
Corrections
- Correction de bugs sur les délais

### 0.1.0-beta.8 - 2025/10
Améliorations
- Ajout de la gestion du son sur un soundboard partagé (stocké uniquement côté support via un cookie)
- Sauvegarde des durées des musiques en BDD pour gagner en performance. 

Corrections
- Fix sur les images des contenus reportables qui n'apparaissaient pas
- Ajout de logs pour corriger des bugs de production sur les pistes de musique
- tentative de correction des fadeOut en prod

Fiabilité & Confiance
- Augmentation de la couverture des tests unitaires
- Création de tests d'intégration pour les routes

### 0.1.0-beta.9 - 2025/10
Corrections
- Fix de l'affichage du bouton pour le réglage du son des musiques partagées

### 0.1.0-beta.10 - 2025/10
Améliorations
- Utilisation de Redis pour le système de cache applicatif

Nouveautés
- Ajout de paramètres de customisation pour les fondus d'entrée et de sortie

Fiabilité & Confiance
- Modification de la structure pour respecter le DDD


### 0.2.0-beta.1 - 2025/11
Nouveautés
- Ajout d'analytics pour avoir des stats sur les utilisateurs (provenance et rétention)
- Ajout de fade-out court lorsque l'on stoppe une musique 
- Ajout d'un badge pour indiquer le nombre de musiques dans une playlist
- Rendre accessible le volume d'une playlist depuis les soundboards publics 
- Possibilité de choisir de sauvegarder le volume d'une playlist ou juste de le modifier pour cette partie
- Actualisation des volumes côté joueurs en cas de rechargement de la page maître 


### 0.2.1 - 2025/11
Améliorations
- Réduction du boutons pour afficher/masquer les mixers d'un boutons

Corrections
- Bugs lors de boutons pour remarque les mixers d'un soundboard publique


### X.Y.Z - Date
Chaque future version utilisera ce format simple :
Nouveautés
- …

Améliorations
- …

Corrections
- …

Fiabilité & Confiance
- …

Prochain Focus
- …