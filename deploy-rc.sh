#!/bin/bash
# Script de déploiement pour AmbianceBoard
# Ce script effectue un déploiement automatisé en production

set -e  # Arrêter le script en cas d'erreur

echo "🔄 Sauvegarde des modifications locales..."
git stash

echo "📥 Récupération des dernières modifications..."
git pull

echo "🐳 Arret des container..."
docker compose -f docker-compose.prod.yml down

echo "suppression des dossier static"
rm -rf staticfiles/

echo "🔧 Configuration des permissions..."
chmod +x ./app/entrypoint.sh
chmod +x ./app/entrypoint.prod.sh

echo "🐳 Build des conteneurs Docker..."
docker compose -f docker-compose.prod.yml build

echo "🚀 Démarrage des conteneurs..."
docker compose -f docker-compose.prod.yml up -d

echo "🧹 Nettoyage des conteneurs et images obsolètes..."
docker container prune -f
docker image prune -f

echo "✅ Déploiement terminé avec succès!"
