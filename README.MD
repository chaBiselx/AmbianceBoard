# AmbianceBoard  
**Soundboard pour jeux de rôle (TTRPG)**  

AmbianceBoard est une soundboard conçue pour les jeux de rôle, permettant d'ajouter :  
- 🔫 **Sons instantanés** : bruits d'armes, cris, etc.  
- 🌊 **Sons d'ambiance** : bruits de mer, feu de camp…  
- 🎶 **Musiques** : musiques de combat, moments dramatiques…  

## 🚀 Fonctionnalités  
✅ Soundboards privées ou publiques  
✅ Gestion de playlists aléatoires  
✅ Déploiement via Docker  

## 📊 SonarCloud  
[![Quality Gate](https://sonarcloud.io/api/project_badges/measure?project=chaBiselx_AmbianceBoard&metric=alert_status)](https://sonarcloud.io/project/overview?id=chaBiselx_AmbianceBoard)  
👉 [Voir le rapport SonarCloud](https://sonarcloud.io/project/overview?id=chaBiselx_AmbianceBoard)  

## 🏗️ Installation  

### 1. Créer un fichier `.env`  
```shell  
cp .env.dev.sample .env  
```  

### 2. Lancer Docker  
```shell  
docker compose up --build  
```  

sous WSL en cas d'erreur avec l'entrypoint utiliser dos2unix
```shell
dos2unix ./app/entrypoint.sh
```

### 3. Accéder au conteneur  
```shell  
docker exec -it AmbianceBoard-back-1 bash  
```  

### 4. Créer un super utilisateur  
```shell  
python manage.py createsuperuser  
```  

## 🔗 URLs utiles  
- 🚀 **Application** : [http://localhost:9999/](http://localhost:9999/)  
- 🐰 **RabbitMQ** : [http://localhost:15672/](http://localhost:15672/)  
- 📬 **MailHog** : [http://localhost:8025/](http://localhost:8025/)  

## 🤝 Contribuer  
1. Fork le projet  
2. Crée une branche (`git checkout -b feature/ma-fonctionnalite`)  
3. Fais un commit (`git commit -m 'Ajout d'une nouvelle fonctionnalité'`)  
4. Push la branche (`git push origin feature/ma-fonctionnalite`)  
5. Crée une Pull Request  

## 📝 Licence  
Ce projet est sous licence **MIT**.  
