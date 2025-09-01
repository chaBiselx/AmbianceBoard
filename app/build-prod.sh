#!/bin/bash

# Script pour builder l'image de production avec le bon .dockerignore

echo "Building production image with production .dockerignore..."

# Sauvegarder le .dockerignore actuel s'il existe
if [ -f ".dockerignore" ]; then
    mv .dockerignore .dockerignore.dev.backup
fi

# Copier le .dockerignore de production
cp .dockerignore.prod .dockerignore

# Builder l'image
docker-compose -f ../docker-compose.prod.yml build --no-cache

# Restaurer le .dockerignore de développement
if [ -f ".dockerignore.dev.backup" ]; then
    mv .dockerignore.dev.backup .dockerignore
else
    rm .dockerignore
fi

echo "Production build completed."
