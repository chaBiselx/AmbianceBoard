all command 
python manage.py


Creer un superutilisateur
python manage.py createsuperuser

make migration 
python manage.py makemigrations

execute migration
python manage.py migrate

Purge BDD
python manage.py sqlflush


lancer les commandes 
python manage.py runcrons

python manage.py crontab add
python manage.py crontab show


dauns premier console 
killall cron
cron -f -L 15 start


ls -la /var/log

crontab -e
* * * * * echo "$(date +"%T") Hello from crontab" >> /var/log/test.log


psql -U postgres
\l 
\c postgres



uuid_generate_v4() => CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
INSERT INTO home_finaluser (id,  email, "userID")
VALUES (uuid_generate_v4(), 'exemple@domaine.com', 'uniqueID123');


purger la BDD et refaire le fichier de migration initial

PSQL 
```
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
```

python 
```
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc" -delete
python manage.py makemigrations
python manage.py migrate
```