# Jeux de non-régression audio

Ajoutez ici des échantillons audio dont vous avez vérifié les labels attendus.
Le jeu est indépendant du modèle : les cas ne décrivent que le fichier, les
labels de référence et le nombre de résultats à examiner.

1. Placez les fichiers sous `audio/` (formats acceptés : WAV, MP3, OGG, FLAC,
   M4A et WebM).
2. Ajoutez un cas dans `manifest.json` :

   ```json
   {
     "cases": [
       {
         "id": "ambiance-foret-nocturne",
         "audio": "audio/foret-nocturne.wav",
         "expected_labels": {
           "environment": ["night-forest"],
           "weather": ["calm-night"]
         },
         "top_k_per_category": 3
       }
     ]
   }
   ```

`audio` est relatif à ce dossier. Chaque label attendu doit apparaître parmi
les `top_k_per_category` premiers résultats de sa catégorie. Les catégories et
labels doivent exister dans le catalogue du service. Le nombre de résultats
est compris entre 1 et 10 ; il doit être au moins égal au nombre de labels
attendus dans chaque catégorie.

Lancez `make test-music-labeler-ti` depuis la racine du dépôt. Le test démarre
le vrai pipeline du service (chargement audio, classification et modèle
configuré), sans remplacer le modèle par un faux. Si le manifeste ne contient
aucun cas, pytest indique que le test est ignoré ; aucun modèle n'est chargé.

Ne versionnez les fichiers audio que si leur licence le permet. Pour que ces
régressions soient vérifiées en CI et par les autres développeurs, les fichiers
référencés doivent être disponibles dans leur environnement de test.
