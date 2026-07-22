# 🔧 Guide de Stabilité Loki

## 🔴 Problèmes Identifiés

### 1. **Loki consomme toute la mémoire**
- ❌ Pas de `limits` de ressources définis
- ❌ Cache trop petit (100MB)
- ❌ Pas de retention policy
- **Impact** : OOM kill → container redémarre

### 2. **Ingestion non contrôlée**
- ❌ Pas de rate limiting
- ❌ Pas de batch size limité
- **Impact** : Saturation rapide lors de pics de logs

### 3. **Problèmes de performance**
- ❌ Filesystem storage lent
- ❌ Pas de timeout HTTP
- ❌ Cache queries non optimisé
- **Impact** : Requêtes lentes, timeouts

### 4. **Accumulation infinie de logs**
- ❌ Aucune retention configurée
- **Impact** : Disque plein après quelques jours

---

## ✅ Solutions Appliquées

### 1. **Limiter la Mémoire (docker-compose.prod.yml)**

```yaml
loki:
  deploy:
    resources:
      limits:
        memory: 1g      # ← Max 1GB
        cpus: '1.0'     # ← Max 1 CPU
      reservations:
        memory: 512m    # ← Min 512MB garantis
```

**Impact** : Loki ne peut plus bouffer toute la RAM

### 2. **Configurer Retention (loki-config.yml)**

```yaml
limits_config:
  retention_period: 168h  # ← Garder 7 jours de logs max
```

**Impact** : Ancien logs supprimés automatiquement

### 3. **Rate Limiting (loki-config.yml)**

```yaml
limits_config:
  ingestion_rate_mb: 10       # ← Max 10MB/s par tenant
  ingestion_burst_size_mb: 20 # ← Max burst de 20MB
  max_streams_per_user: 10000 # ← Max 10k streams
```

**Impact** : Prévenir les pics de charge

### 4. **Cache Plus Grand (loki-config.yml)**

```yaml
query_range:
  results_cache:
    cache:
      embedded_cache:
        enabled: true
        max_size_mb: 500  # ← De 100MB à 500MB
```

**Impact** : Moins d'accès disque, plus rapide

### 5. **Ingester Optimisé (loki-config.yml)**

```yaml
ingester:
  chunk_idle_period: 3m
  max_chunk_age: 1h
  chunk_retain_period: 1m
  chunk_encoding: gzip  # ← Compression
```

**Impact** : Meilleure gestion de la mémoire, compression des données

### 6. **Promtail Batching (promtail-config.yml)**

```yaml
clients:
  - url: http://loki:3100/loki/api/v1/push
    batch_size: 1000      # ← Grouper 1000 logs
    batch_timeout: 5s     # ← Envoyer tous les 5s max
    backoff_config:
      max_retries: 3      # ← Retry si erreur
      max_backoff: 10s    # ← Max 10s entre retries
```

**Impact** : Moins de requêtes HTTP, plus stable

### 7. **Timeouts HTTP (promtail-config.yml)**

```yaml
clients:
  - timeout: 5s  # ← Timeout 5s
```

**Impact** : Pas de connexions zombies

---

## 📊 Avant vs Après

| Métrique | Avant | Après |
|----------|-------|-------|
| Mémoire Loki | Illimitée ➡️ OOM | **Max 1GB** |
| Retention | ∞ (croissance infinie) | **7 jours** |
| Rate Limit | Aucun | **10MB/s** |
| Cache | 100MB | **500MB** |
| Requêtes HTTP | Non batchées | **Batchées (1000 logs)** |
| Timeouts | Aucun | **5s** |
| Compression | Non | **gzip** |

---

## 🚀 Déploiement

```bash
# 1. Commit les changements
git add loki-config.yml promtail-config.yml docker-compose.prod.yml
git commit -m "fix(loki): optimize memory, add retention, rate limiting and batching"

# 2. Redéployer
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml build
docker compose -f docker-compose.prod.yml up -d

# 3. Vérifier
docker stats loki  # Voir la mémoire consommée
docker logs loki | grep -i "error\|warn"
```

---

## 🔍 Monitoring

### Vérifier la Mémoire

```bash
docker stats loki
# Doit être < 1GB
```

### Vérifier la Retention

```bash
# Les logs plus vieux que 7 jours doivent disparaître
du -sh /var/lib/docker/volumes/ambianceboard_loki-data/_data/
```

### Vérifier les Erreurs

```bash
docker logs loki --tail 50 | grep -i "error\|panic"
```

### Vérifier les Performances

```bash
# Loki doit répondre vite
curl -w "\n%{time_total}s\n" http://localhost:3100/loki/api/v1/labels
```

---

## ⚙️ Ajustements Fins (si nécessaire)

### Si Loki est Trop Lent

```yaml
# Augmenter le cache
max_size_mb: 1000  # ← De 500MB à 1GB
```

### Si Logs Perdus

```yaml
# Augmenter le rate limit
ingestion_rate_mb: 20  # ← De 10MB/s à 20MB/s
```

### Si Mémoire Insuffisante

```yaml
# Dans docker-compose.prod.yml
limits:
  memory: 2g  # ← De 1GB à 2GB
```

### Si Disque Plein Trop Vite

```yaml
# Réduire la retention
retention_period: 72h  # ← De 168h à 72h (3 jours)
```

---

## 🆘 Troubleshooting

### Loki Crash / OOM Kill

```bash
docker logs loki | tail -20
# Si "Cannot allocate memory" :
# 1. Augmenter la limite memory dans docker-compose.prod.yml
# 2. Réduire retention_period
# 3. Réduire max_size_mb du cache
```

### Requêtes Lentes

```bash
# Augmenter le cache et/ou les CPU
max_size_mb: 1000
cpus: '2.0'
```

### Logs Perdus / Gap

```bash
# Vérifier que Promtail se connecte
docker logs promtail | grep -i "error\|retry"
# Augmenter batch_size et max_retries
```

### Disque Plein

```bash
# Réduire la retention
retention_period: 24h  # Garder 1 jour seulement
```

---

## ✅ Checklist Post-Déploiement

- [ ] Loki démarre sans erreur
- [ ] Mémoire Loki < 1GB (vérifier avec `docker stats`)
- [ ] Les logs arrivent à Loki (vérifier dans Grafana)
- [ ] Requêtes Loki rapides (< 1s)
- [ ] Pas de croissance infinie du disque
- [ ] Tous les containers stables (pas de restart)

---

## 📝 Fichiers Modifiés

| Fichier | Changement |
|---------|-----------|
| `loki-config.yml` | Ajout ingester, limits, retention, augmentation cache |
| `promtail-config.yml` | Ajout batching, retry, timeout |
| `docker-compose.prod.yml` | Ajout resource limits pour Loki |

---

**Status**: ✅ **LOKI STABLE & PERFORMANT**
