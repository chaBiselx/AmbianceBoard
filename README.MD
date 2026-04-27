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
![Quality Gate](https://sonarcloud.io/api/project_badges/measure?project=chaBiselx_AmbianceBoard&metric=alert_status) 
![Security](https://sonarcloud.io/api/project_badges/measure?project=chaBiselx_AmbianceBoard&metric=security_rating)
![Reliability](https://sonarcloud.io/api/project_badges/measure?project=chaBiselx_AmbianceBoard&metric=reliability_rating) 
![Maintainability](https://sonarcloud.io/api/project_badges/measure?project=chaBiselx_AmbianceBoard&metric=sqale_rating) 
![Duplication](https://sonarcloud.io/api/project_badges/measure?project=chaBiselx_AmbianceBoard&metric=duplicated_lines_density)  
👉 [Voir le rapport SonarCloud](https://sonarcloud.io/project/overview?id=chaBiselx_AmbianceBoard)  

## 🤝 Avancement 
Suivi du projet
[clickUp](https://sharing.clickup.com/9014791178/l/h/8cn5k0a-554/d11e2ded9d8d1d4)

## 🏗️ Installation  

### 1. Créer un fichier `.env`  
```shell  
cp .env.dev.sample .env  
```  

### 2. Lancer Docker  
```shell  
make build
```  

sous WSL en cas d'erreur avec l'entrypoint utiliser dos2unix
```shell
dos2unix ./app/entrypoint.sh
```

ou 
```shell
find . -type f -print0 | xargs -0 dos2unix
```

### 3. Accéder au conteneur  
```shell  
make enter S=back
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

## Architecture 

### Backend 

DDD
```
app/main/
├── application/
│   ├── auth/
│   └── helper/
├── domain
│   ├── common/
│   │   ├── decorator/
│   │   ├── enum/
│   │   ├── exceptions/
│   │   ├── factory/
│   │   ├── helper/
│   │   ├── mixins/
│   │   ├── service/
│   │   ├── strategy/
│   │   └── utils/
│   │       ├── EmailSender, ImageResizer, AudioDurationUtils
│   │       ├── cache/ (système de cache)
│   │       ├── logger/ (logging)
│   │       └── settings/ (configuration)
│   │
│   ├── general/
│   │   └── service/ 
│   ├── private/
│   │   ├── dto/
│   │   ├── formatter/
│   │   ├── manager/
│   │   └── service/
│   ├── public/
│   │   ├── decorator/
│   │   └── service/
│   ├── manager/
│   │   ├── decorator/
│   │   └── service/
│   ├── moderator/
│   │   ├── dto/
│   │   └── service/
│   ├── brokers/
│   │   ├── message/
│   │   ├── service/
│   │   └── strategy/
│   ├── cron/
│   │   ├── cronFile/
│   │   └── service/
│   └── sharedSoundboard/
│       └── consummers/
│
├── interface
│   ├── ui/
│   │   ├── controller/
│   │   │   ├── general/
│   │   │   ├── private/
│   │   │   ├── public/
│   │   │   ├── manager/
│   │   │   ├── moderator/
│   │   │   └── sharedSoundboard/
│   │   ├── forms/
│   │   │   ├── general/
│   │   │   ├── private/
│   │   │   ├── manager/
│   │   │   └── moderator/
│   │   ├── seo/
│   │   ├── templates/
│   │   └── templatetags/
│   │
│   └── admin/
│
├── architecture
│   ├── persistence/
│   │   ├── models/
│   │   ├── repository/
│   │   ├── migrations/
│   │   └── postMigrate/
│   │
│   ├── messaging/
│   │   ├── email/
│   │   │   ├── UserMail.py
│   │   │   └── ModeratorEmail.py
│   │   ├── tasks/
│   │   │   └── celery.py
│   │   └── events/
│   │       └── signals.py
│   │
│   ├── middleware/
│   │   ├── DailySessionMiddleware.py
│   │   ├── ErrorTrackingMiddleware.py
│   │   └── LogRequestsMiddleware.py
│   │
│   └── contextProcessors/
│       ├── general_information_processor.py
│       ├── sidebar_processor.py
│       └── user_preference_processor.py
├── TNR/
│   ├── TU/ (Tests Unitaires)
│   ├── TI/ (Tests d'Intégration)
│   └── Fixtures/
│
├── models.py
└── apps.py
```

