#!/bin/bash

# Script de déploiement Nginx pour ambianceboard.com
# Configuration automatique pour VPS

set -e

echo "🚀 Configuration Nginx pour ambianceboard.com"
echo "============================================="

# Variables prédéfinies
DOMAIN="ambianceboard.com"
read -p "Entrez votre email pour Let's Encrypt: " EMAIL
read -p "Port de votre application Django (défaut: 8080): " DJANGO_PORT
DJANGO_PORT=${DJANGO_PORT:-8080}

# Vérification des prérequis
echo "📋 Vérification des prérequis..."

if ! command -v nginx &> /dev/null; then
    echo "❌ Nginx n'est pas installé. Installation..."
    sudo apt update
    sudo apt install -y nginx
fi

if ! command -v certbot &> /dev/null; then
    echo "❌ Certbot n'est pas installé. Installation..."
    sudo apt install -y certbot python3-certbot-nginx
fi

# Création des répertoires nécessaires
echo "📁 Création des répertoires..."
sudo mkdir -p /var/www/certbot
sudo mkdir -p /var/log/nginx

# Sauvegarde de la configuration nginx existante
if [ -f /etc/nginx/sites-available/default ]; then
    echo "💾 Sauvegarde de la configuration nginx existante..."
    sudo cp /etc/nginx/sites-available/default /etc/nginx/sites-available/default.backup.$(date +%Y%m%d_%H%M%S)
fi

# Création de la configuration nginx temporaire (sans SSL)
echo "⚙️  Création de la configuration nginx temporaire..."
sudo tee /etc/nginx/sites-available/ambianceboard-temp > /dev/null <<EOF
server {
    listen 80;
    server_name ${DOMAIN} www.${DOMAIN};
    
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
        try_files \$uri =404;
    }
    
    location /health-check {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
    
    location / {
        proxy_pass http://127.0.0.1:${DJANGO_PORT};
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# Activation de la configuration temporaire
sudo ln -sf /etc/nginx/sites-available/ambianceboard-temp /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test de la configuration nginx temporaire
echo "🧪 Test de la configuration nginx temporaire..."
sudo nginx -t

if [ $? -ne 0 ]; then
    echo "❌ Erreur dans la configuration nginx temporaire"
    exit 1
fi

# Redémarrage de nginx
echo "🔄 Redémarrage de nginx..."
sudo systemctl restart nginx
sudo systemctl enable nginx

# Vérification que le site répond en HTTP
echo "🌐 Vérification de la connectivité HTTP..."
sleep 2
if curl -s --max-time 10 "http://${DOMAIN}/health-check" | grep -q "healthy"; then
    echo "✅ Site accessible en HTTP"
else
    echo "⚠️  Site non accessible en HTTP - continuons quand même..."
fi

# Obtention du certificat SSL
echo "🔒 Obtention du certificat SSL Let's Encrypt..."
sudo certbot certonly --webroot -w /var/www/certbot -d ${DOMAIN} -d www.${DOMAIN} --email ${EMAIL} --agree-tos --no-eff-email

# Vérification que le certificat a été créé
if [ -f "/etc/letsencrypt/live/${DOMAIN}/fullchain.pem" ]; then
    echo "✅ Certificat SSL créé avec succès"
else
    echo "❌ Erreur lors de la création du certificat SSL"
    exit 1
fi

# Configuration des chemins statiques et média
echo "📝 Configuration des chemins statiques..."
read -p "Chemin vers vos fichiers statiques (ex: /home/user/app/staticfiles): " STATIC_PATH
read -p "Chemin vers vos fichiers média (ex: /home/user/app/mediafiles): " MEDIA_PATH

# Vérification que le fichier ngix.prod existe
if [ ! -f "ngix.prod" ]; then
    echo "❌ Fichier ngix.prod non trouvé dans le répertoire courant"
    echo "📁 Répertoire courant: $(pwd)"
    echo "📂 Fichiers disponibles: $(ls -la)"
    exit 1
fi

# Copie et configuration du fichier final avec SSL
echo "🔧 Création de la configuration nginx finale avec SSL..."
sudo cp ngix.prod /etc/nginx/sites-available/ambianceboard

# Mise à jour des chemins dans la configuration
if [ ! -z "$STATIC_PATH" ]; then
    sudo sed -i "s|/path/to/your/staticfiles/|${STATIC_PATH}/|g" /etc/nginx/sites-available/ambianceboard
fi

if [ ! -z "$MEDIA_PATH" ]; then
    sudo sed -i "s|/path/to/your/mediafiles/|${MEDIA_PATH}/|g" /etc/nginx/sites-available/ambianceboard
fi

# Mise à jour du port Django si différent de 8000
if [ "$DJANGO_PORT" != "8000" ]; then
    sudo sed -i "s|127.0.0.1:8000|127.0.0.1:${DJANGO_PORT}|g" /etc/nginx/sites-available/ambianceboard
fi

# Test de la configuration finale
echo "🧪 Test de la configuration nginx finale..."
sudo nginx -t

if [ $? -eq 0 ]; then
    echo "✅ Configuration nginx valide"
    
    # Activation de la configuration finale
    sudo ln -sf /etc/nginx/sites-available/ambianceboard /etc/nginx/sites-enabled/
    sudo rm -f /etc/nginx/sites-enabled/ambianceboard-temp
    
    # Redémarrage final
    echo "🔄 Redémarrage final de nginx..."
    sudo systemctl reload nginx
else
    echo "❌ Erreur dans la configuration nginx finale"
    echo "🔍 Vérification des logs d'erreur:"
    sudo nginx -t
    exit 1
fi

# Configuration du renouvellement automatique des certificats
echo "🔄 Configuration du renouvellement automatique des certificats..."
sudo tee /etc/cron.d/certbot-renew > /dev/null <<EOF
0 12 * * * root certbot renew --quiet --post-hook "systemctl reload nginx"
EOF

# Vérification du firewall
echo "🔥 Configuration du firewall..."
if command -v ufw &> /dev/null; then
    sudo ufw allow 'Nginx Full'
    sudo ufw allow OpenSSH
    echo "ℹ️  Pour activer le firewall: sudo ufw enable"
fi

# Test final de connectivité HTTPS
echo "🔒 Test final de connectivité HTTPS..."
sleep 3
if curl -s --max-time 10 "https://${DOMAIN}/health-check" | grep -q "healthy"; then
    echo "✅ Site accessible en HTTPS"
else
    echo "⚠️  Site non accessible en HTTPS - vérifiez votre application Django"
fi

echo ""
echo "🎉 Configuration terminée avec succès !"
echo "======================================"
echo "🌐 Votre site: https://${DOMAIN}"
echo "🔒 Certificats SSL: ✅ Installés"
echo "🔄 Renouvellement auto: ✅ Configuré"
echo ""
echo "🧪 Tests de validation:"
echo "   curl https://${DOMAIN}/health-check"
echo "   curl https://${DOMAIN}/ssl-test"
echo ""
echo "📋 Commandes utiles:"
echo "   sudo systemctl status nginx"
echo "   sudo nginx -t"
echo "   sudo certbot certificates"
echo "   sudo tail -f /var/log/nginx/ambianceboard_access.log"
echo "   sudo tail -f /var/log/nginx/ambianceboard_error.log"
echo ""
echo "🌟 Pour tester complètement:"
echo "   ./test-nginx-ssl.sh ambianceboard.com"
echo ""
echo "⚠️  N'oubliez pas de:"
echo "   1. ✅ DNS configuré pour pointer vers votre VPS"
echo "   2. 🐍 Application Django démarrée sur le port ${DJANGO_PORT}"
echo "   3. 📁 Chemins static/media corrects: ${STATIC_PATH} / ${MEDIA_PATH}"
echo "   4. 🔧 ALLOWED_HOSTS dans Django avec 'ambianceboard.com'"
