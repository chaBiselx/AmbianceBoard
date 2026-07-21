# Fix pour Gunicorn Worker Timeout Issue

## Problème Diagnostiqué
```
[2026-07-21 20:44:08 +0000] [1] [CRITICAL] WORKER TIMEOUT (pid:23)
Exception ignored while calling deallocator <function CompositeLogger.__del__>
  File ".../LokiLogger.py", line 243, in shutdown
    self._sender_thread.join(timeout=5.0)
[2026-07-21 20:44:09 +0000] [1] [ERROR] Worker (pid:23) was sent SIGKILL! Perhaps out of memory?
```

### Causes Racines
1. **Timeout Gunicorn non configuré** : utilise le défaut de 30 secondes
2. **Logger shutdown trop long** : 
   - `flush()` attendait jusqu'à 10 secondes
   - `join(timeout=5s)` attendait le thread Loki
   - Total potentiel : 15+ secondes > 30s timeout
3. **Appel depuis __del__** : blocage pendant la garbage collection

## Corrections Appliquées

### 1. ✅ Augmenter le timeout Gunicorn (docker-compose.prod.yml)
```bash
# Avant
command: gunicorn ... --workers=3 --max-requests=1000

# Après
command: gunicorn ... --workers=3 --max-requests=1000 --timeout=60
```
**Impact** : Laisse 60 secondes au worker pour arrêter proprement

### 2. ✅ Réduire les timeouts du logger (app/main/domain/common/utils/logger/LokiLogger.py)
```python
# flush() timeout : 10s → 5s
timeout = 5.0  # au lieu de 10.0

# join() timeout : 5s → 2s
self._sender_thread.join(timeout=2.0)  # au lieu de 5.0
```
**Impact** : Réduit le temps d'arrêt total à ~7 secondes maximum

### 3. ✅ Améliorer la robustesse du shutdown (LokiLogger.py et CompositeLogger.py)
- Ajouter try/except autour du flush() et join()
- Ajouter un timeout global dans CompositeLogger.shutdown() (10s max)
- Éviter les blocages non rattrapés

### 4. ✅ Signal handling pour arrêt gracieux (app/parameters/wsgi.py)
- Enregistrer SIGTERM et SIGINT handlers
- Appeler `logger.shutdown()` avant la terminaison
- Permet à Gunicorn de notifier le worker pour qu'il s'arrête proprement

### 5. ✅ Configuration Gunicorn explicite (app/gunicorn_config.py)
- Documenter les meilleures pratiques
- Permet l'utilisation via : `gunicorn -c app/gunicorn_config.py`
- Variables d'env pour les timeouts

## Déploiement

### Option 1 : Redéployer avec docker-compose (recommandé)
```bash
./deploy.sh  # ou
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml build
docker compose -f docker-compose.prod.yml up -d
```

### Option 2 : Modification rapide (à chaud)
```bash
# Dans le container
docker exec ambianceboard-back-1 bash
# Éditer ou redémarrer le service
```

## Vérification

Après le déploiement :
```bash
# Vérifier les logs Gunicorn
docker logs ambianceboard-back-1 | tail -100

# Chercher les timeouts
docker logs ambianceboard-back-1 | grep -i "timeout\|sigkill\|worker"

# Vérifier que les services Loki répondent
curl http://your-loki-url:3100/loki/api/v1/labels
```

## Résumé des Changements
| Fichier | Changement |
|---------|-----------|
| `docker-compose.prod.yml` | Ajouter `--timeout=60` à Gunicorn |
| `LokiLogger.py` | Réduire flush: 10s→5s, join: 5s→2s, ajouter try/except |
| `CompositeLogger.py` | Ajouter timeout global (10s) au shutdown |
| `parameters/wsgi.py` | Ajouter signal handlers pour arrêt gracieux |
| `app/gunicorn_config.py` | Nouvelle config (optionnel mais recommandé) |

## Métriques Attendues
- ✅ Pas plus de timeout worker
- ✅ Shutdown < 7 secondes (< 60s limit)
- ✅ Logs correctement envoyés à Loki avant shutdown
- ✅ Worker tue proprement sans SIGKILL
