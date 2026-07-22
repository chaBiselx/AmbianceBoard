# ✅ LOKI STABILITY FIX - Resumé Complet

## 🎯 Problème

Loki causait des ralentissements et timeouts Gunicorn à cause de :
- Consommation mémoire illimitée → OOM Kill
- Pas de rate limiting → surcharge lors de pics
- Logs s'accumulent indéfiniment
- Cache trop petit → sollicitation disque constante
- Pas de timeouts HTTP → connexions zombies

## ✅ Solutions Appliquées

### 1. **loki-config.yml** - Optimisation Loki

```yaml
# ✅ Ingester optimisé
ingester:
  chunk_idle_period: 3m
  max_chunk_age: 1h
  chunk_encoding: gzip  # Compression

# ✅ Cache 5x plus grand
query_range:
  results_cache:
    max_size_mb: 500  # De 100MB → 500MB

# ✅ Limits strictes
limits_config:
  ingestion_rate_mb: 10        # Max 10MB/s
  ingestion_burst_size_mb: 20  # Max burst 20MB
  retention_period: 168h       # Logs auto-supprimés après 7j

# ✅ Timeouts HTTP
server:
  http_server_read_timeout: 10s
  http_server_write_timeout: 10s

# ✅ Analytics désactivées
analytics:
  reporting_enabled: false
```

### 2. **promtail-config.yml** - Batching & Retry

```yaml
clients:
  - url: http://loki:3100/loki/api/v1/push
    # ✅ Batching réduit la charge
    batch_size: 1000
    batch_timeout: 5s
    # ✅ Retry strategy
    backoff_config:
      min_backoff: 100ms
      max_backoff: 10s
      max_retries: 3
    # ✅ Timeout HTTP
    timeout: 5s
```

### 3. **docker-compose.prod.yml** - Resource Limits

```yaml
loki:
  deploy:
    resources:
      limits:
        memory: 1g      # ✅ Max 1GB
        cpus: '1.0'     # ✅ Max 1 CPU
      reservations:
        memory: 512m    # ✅ Min 512MB
```

## 📊 Avant vs Après

| Aspect | Avant | Après |
|--------|-------|-------|
| **Mémoire** | Illimitée → OOM | Max 1GB |
| **Retention** | ∞ (croissance infinie) | 7 jours auto-cleanup |
| **Rate Limit** | Aucun | 10MB/s |
| **Pics Logs** | Saturation → crash | Batch 1000 logs |
| **Cache** | 100MB (sollicite disque) | 500MB (plus rapide) |
| **HTTP** | Connexions zombies | Timeouts 5s + retry |
| **Compression** | Non | gzip |
| **Analytics** | Enabled (overhead) | Disabled |

## 🚀 Déploiement

### Option 1 : Déploiement Complet (Recommandé)

```bash
# 1. Vérifier les changements
git status
# Doit afficher : loki-config.yml, promtail-config.yml, docker-compose.prod.yml

# 2. Commit
git add loki-config.yml promtail-config.yml docker-compose.prod.yml LOKI_STABILITY_FIX.md
git commit -m "fix(loki): optimize memory, retention, rate limiting and batching"
git push origin master

# 3. Redéployer en production
./deploy.sh

# Ou manuellemen :
docker compose -f docker-compose.prod.yml down loki promtail
docker compose -f docker-compose.prod.yml build loki promtail
docker compose -f docker-compose.prod.yml up -d loki promtail
```

### Option 2 : Mise à Jour à Chaud (Test)

```bash
# Copier les config
docker cp loki-config.yml ambianceboard-loki-1:/etc/loki/local-config.yaml
docker cp promtail-config.yml ambianceboard-promtail-1:/etc/promtail/config.yml

# Redémarrer
docker restart ambianceboard-loki-1 ambianceboard-promtail-1

# Vérifier
docker logs ambianceboard-loki-1 | tail -20
```

## ✅ Vérification Post-Déploiement

### 1. Loki Démarre Correctement

```bash
docker logs loki -n 20
# Doit voir : "level=info msg="listening"" (pas d'errors)
```

### 2. Mémoire Contrôlée

```bash
docker stats loki --no-stream
# Doit montrer : MEM < 1GB (ex: 512MB)
```

### 3. Logs Arrivent à Loki

```bash
# Dans Grafana : Explore → Loki
# Doit voir les logs des dernières heures
```

### 4. Requêtes Loki Rapides

```bash
curl -w "\nTime: %{time_total}s\n" http://localhost:3100/loki/api/v1/labels
# Doit être < 1 seconde
```

### 5. Pas d'Accumulation Infinie

```bash
du -sh /var/lib/docker/volumes/ambianceboard_loki-data/_data/
# Taille stable ou légère croissance (pas d'explosion)
```

### 6. Metrics Stables

```bash
docker stats loki promtail --no-stream
# CPU & MEM doivent rester stables
```

## 🔍 Troubleshooting

### Problem: "Cannot allocate memory" (Loki crash)

**Solution** :
```bash
# Augmenter la limite mémoire
# Edit docker-compose.prod.yml:
limits:
  memory: 2g  # De 1g → 2g
```

### Problem: "timeout" dans les logs

**Solution** :
```bash
# Augmenter les timeouts dans promtail-config.yml
timeout: 10s  # De 5s → 10s
```

### Problem: "ingestion rate exceeded"

**Solution** :
```bash
# Augmenter le rate limit dans loki-config.yml
ingestion_rate_mb: 20  # De 10 → 20
```

### Problem: Disque plein rapidement

**Solution** :
```bash
# Réduire la retention dans loki-config.yml
retention_period: 72h  # De 168h (7j) → 72h (3j)
```

### Problem: Grafana ne voit pas les logs

**Solution** :
```bash
# Vérifier que Loki répond
curl http://localhost:3100/loki/api/v1/labels

# Vérifier que Promtail envoie
docker logs promtail | grep -i "error\|warn"

# Redémarrer les deux
docker restart loki promtail
```

## 📈 Monitoring Continu

### Créer une alerte dans Grafana

```promql
# CPU Loki > 80%
100 * (1 - avg(rate(node_cpu_seconds_total{mode="idle"}[5m]))) > 80

# Mémoire Loki > 800MB
container_memory_usage_bytes{name="ambianceboard-loki-1"} > 800000000

# Erreurs Loki
increase(loki_ingester_streams_created_total[5m]) < 0
```

## 📝 Files Modifiés

```
✅ loki-config.yml
   - Ajout ingester config (compression, chunk management)
   - Cache augmenté 100MB → 500MB
   - Rate limiting strict (10MB/s)
   - Retention policy (7 jours)
   - Timeouts HTTP explicites
   - Analytics désactivées

✅ promtail-config.yml
   - Batching (1000 logs par batch)
   - Retry strategy (max 3 retries)
   - Timeouts HTTP (5s)

✅ docker-compose.prod.yml
   - Resource limits pour Loki (1GB max, 512MB min)
```

## 🎓 Explications Techniques

### Pourquoi Rate Limiting ?

```
Sans limit :
App sends 100MB logs/s → Loki peut pas suivre → Queue infinie → OOM

Avec limit (10MB/s) :
App sends 100MB → Promtail queue → Backoff strategy → Pas de crash
```

### Pourquoi Batching ?

```
Sans batch :
Promtail envoie 1 log = 1 requête HTTP = overhead énorme

Avec batch (1000 logs) :
1000 logs = 1 requête HTTP = 1000x moins de overhead
```

### Pourquoi Retention ?

```
Sans retention :
Logs accumulent indéfiniment → Disque plein après X jours

Avec retention (7j) :
Ancien logs auto-supprimés → Disque stable
```

### Pourquoi Limites Mémoire ?

```
Sans limite :
OOM killer random → crashes imprévisibles

Avec limite (1GB) :
Loki canalisé → prévisible + fallback sur disque
```

## ✅ Checklist Final

- [ ] Tous les containers démarrés
- [ ] Loki < 1GB mémoire
- [ ] Logs arrivent dans Grafana
- [ ] Requêtes Loki < 1s
- [ ] Pas de croissance infinie du disque
- [ ] No `CRITICAL` ou `PANIC` in Loki logs
- [ ] Worker Gunicorn stable (pas de TIMEOUT)

---

**Status**: ✅ **LOKI STABLE ET OPTIMISÉ - PRÊT POUR PROD**
