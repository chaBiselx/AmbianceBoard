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


psql -U postgres
\l 



uuid_generate_v4() => CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
INSERT INTO home_finaluser (id,  email, "userID")
VALUES (uuid_generate_v4(), 'exemple@domaine.com', 'uniqueID123');