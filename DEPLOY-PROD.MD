# A faire la premiere fois sur un serveur
## install 
sudo apt install make
sudo apt install docker
sudo apt install ufw
sudo apt install certbot python3-certbot-nginx

cd /srv/www/AmbianceBoard/

git clone https://github.com/chaBiselx/AmbianceBoard.git
git remote set-url --push origin no_push

## confgix nginx 
sudo apt install nginx
sudo vi /etc/nginx/sites-available/ambianceboard

sudo ln -s /etc/nginx/sites-available/ambianceboard /etc/nginx/sites-enabled/
sudo nginx -t

sudo certbot --nginx -d ambianceboard.com -d www.ambianceboard.com
sudo certbot --nginx -d graph.ambianceboard.com -d www.graph.ambianceboard.com

sudo ufw status
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 22/tcp
sudo ufw allow 8000/tcp
sudo ufw allow 3100/tcp
sudo ufw allow 'Nginx Full'

sudo nginx -t
sudo nginx -s reload

# mettre en place le projet 

## metre a jour le .env si besoin 
vi /srv/www/AmbianceBoard/.env

## pull la branch 
cd /srv/www/AmbianceBoard/ && chmod +x deploy.sh && sh deploy.sh

ou manuellement 

cd /srv/www/AmbianceBoard/ && chmod +x app/entrypoint.sh && chmod +x app/entrypoint.prod.sh

## deployement du back (lors de la première fois)
dans le container back

python manage.py makemigrations main
python manage.py migrate main
python manage.py migrate

python manage.py createsuperuser
mettre les roles et les tiers utilisateur a l'admin

# Utiles 

## docker

### build 
docker compose -f docker-compose.prod.yml build --no-cache
docker compose -f docker-compose.prod.yml up

### suppression des container
docker rm -f $(docker ps -aq)



## creation user app
sudo useradd -M -s /bin/bash ambianceboard-app
sudo passwd ambianceboard-app
sudo chown ambianceboard-app:ambianceboard-app /srv/www/AmbianceBoard

