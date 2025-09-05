#!/bin/bash
# Script de déploiement pour AmbianceBoard
# Ce script effectue un déploiement automatisé en production

set -e  # Arrêter le script en cas d'erreur

echo "🔄 Sauvegarde des modifications locales..."
git stash

echo "📥 Récupération des dernières modifications..."
git fetch --tags

# Récupérer le dernier tag ou master si aucun tag n'existe
LATEST_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "")

if [ -n "$LATEST_TAG" ]; then
    echo "🏷️  Checkout du dernier tag: $LATEST_TAG"
    git checkout "$LATEST_TAG"
else
    echo "🌿 Aucun tag trouvé, checkout de master"
    git checkout master
    git pull origin master
fi

echo "🐳 Arret des container..."
docker compose -f docker-compose.prod.yml down

echo "suppression des dossier static"
rm -rf ./statiticfiles/*

echo "🔧 Configuration des permissions..."
chmod +x ./app/entrypoint.sh
chmod +x ./app/entrypoint.prod.sh

echo "🐳 Build des conteneurs Docker..."
docker compose -f docker-compose.prod.yml build

echo "🚀 Démarrage des conteneurs..."
docker compose -f docker-compose.prod.yml up -d

echo "✅ Déploiement terminé avec succès!"
