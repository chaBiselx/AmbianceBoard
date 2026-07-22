# 🚀 DEPLOYMENT GUIDE - Loki Stability Fix

## ✅ Pre-Deployment Checklist

- [ ] Vous êtes sur master ou test-reparation
- [ ] Tous les changements sont committés (`git status` propre)
- [ ] Les configs Loki/Promtail sont valides (pas de syntax errors)
- [ ] Vous avez une sauvegarde de la DB (backup avant deploy)
- [ ] Vous avez accès à la prod (`ssh`)

## 📋 Résumé des Changements

### 3 Fichiers Modifiés

1. **loki-config.yml**
   - ✅ Ajout ingester config (compression, chunk management)
   - ✅ Cache 5x plus grand (100MB → 500MB)
   - ✅ Rate limiting strict (10MB/s)
   - ✅ Retention policy (7 jours auto-cleanup)
   - ✅ Analytics désactivées
   - ✅ Timeouts HTTP explicites

2. **promtail-config.yml**
   - ✅ Batching (1000 logs par batch)
   - ✅ Retry strategy (max 3 retries)
   - ✅ Timeouts HTTP (5s)

3. **docker-compose.prod.yml**
   - ✅ Resource limits pour Loki (max 1GB, min 512MB)
   - ✅ CPU limit (1 core)

### Documentation Ajoutée

- `LOKI_STABILITY_FIX.md` - Guide détaillé des problèmes et solutions
- `LOKI_FIX_SUMMARY.md` - Résumé avec troubleshooting
- `FINAL_TIMEOUT_FIX.md` - Fix du timeout Gunicorn (non-blocking shutdown)

---

## 🚀 Deployment Steps

### STEP 1️⃣ : Verifier les Changements Localement

```bash
# Clone ou fetch le dernier code
git status  # Doit être propre
git log --oneline -5

# Vérifier les fichiers modifiés
git diff master..HEAD -- loki-config.yml | head -30
```

### STEP 2️⃣ : Valider les Configs YAML

```bash
# Vérifier syntaxe Loki
docker run --rm -v $(pwd):/workspace \
  grafana/loki:latest -config.file=/workspace/loki-config.yml \
  -log.level=error > /dev/null && echo "✅ Loki config OK"

# Vérifier Promtail config
docker run --rm -v $(pwd):/workspace \
  grafana/promtail:latest -config.file=/workspace/promtail-config.yml \
  > /dev/null 2>&1 && echo "✅ Promtail config OK"
```

### STEP 3️⃣ : Commit et Push

```bash
# Ajouter les fichiers
git add loki-config.yml promtail-config.yml docker-compose.prod.yml \
        LOKI_STABILITY_FIX.md LOKI_FIX_SUMMARY.md

# Commit
git commit -m "fix(loki): optimize memory, retention, rate limiting and batching

- Add ingester config with gzip compression
- Increase cache from 100MB to 500MB
- Add rate limiting (10MB/s)
- Add retention policy (7 days auto-cleanup)
- Add resource limits (1GB max, 512MB min)
- Add Promtail batching (1000 logs per batch)
- Add retry strategy and HTTP timeouts
- Disable analytics reporting"

# Push
git push origin master
# ou si sur test-reparation :
git push origin test-reparation
```

### STEP 4️⃣ : Backup AVANT Deploy

```bash
# SSH en prod
ssh -i ~/.ssh/id_ed25519_ambianceboard root@82.165.91.41

# Backup Loki data
cd /app/AmbianceBoard
tar -czf backup-loki-$(date +%Y%m%d_%H%M%S).tar.gz \
  /var/lib/docker/volumes/ambianceboard_loki-data

# Backup des configs
tar -czf backup-configs-$(date +%Y%m%d_%H%M%S).tar.gz \
  loki-config.yml promtail-config.yml docker-compose.prod.yml
```

### STEP 5️⃣ : Redeploy

```bash
# Option A : Utiliser le script de déploiement
./deploy.sh

# Option B : Manuel (si on veut contrôler)
docker compose -f docker-compose.prod.yml down loki promtail
docker compose -f docker-compose.prod.yml pull loki promtail
docker compose -f docker-compose.prod.yml up -d loki promtail

# Option C : Full redeploy (si tous les changements)
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml build
docker compose -f docker-compose.prod.yml up -d
```

### STEP 6️⃣ : Vérification Post-Deploy

```bash
# 1. Vérifier que les containers démarrent
docker compose -f docker-compose.prod.yml ps
# Tous les containers doivent être "Up"

# 2. Vérifier les logs Loki
docker logs loki -n 50 | tail -20
# Doit voir : "level=info msg="listening"" (pas d'errors)

# 3. Vérifier la mémoire Loki
docker stats loki --no-stream | grep -E "MEM|LIMIT"
# Doit être < 1GB

# 4. Vérifier que Loki répond
curl -s http://localhost:3100/loki/api/v1/labels | head -c 50
# Doit avoir une réponse JSON

# 5. Vérifier les logs arrivent
docker logs promtail -n 20 | grep -i "error\|warn\|backoff"
# Doit voir que Promtail envoie des logs

# 6. Vérifier le backend
docker logs back-1 | tail -20 | grep -i "timeout\|critical"
# Doit être vide (pas de timeout)
```

---

## 🔍 Monitoring Post-Deployment (24h)

### Heure 1 - Stabilité Immédiate

```bash
# Toutes les 5 min pendant 1h
watch 'docker stats loki promtail --no-stream | grep -E "CONTAINER|loki|promtail"'
```

### Heure 6-24 - Stabilité Long Terme

```bash
# Vérifier chaque heure
# - Mémoire Loki stable
# - Pas d'OOM kills
# - Logs continuent d'arriver
# - Requêtes Loki rapides

# Checker les logs Grafana
docker logs grafana | grep -i error

# Checker les logs du backend
docker logs back-1 | grep -i timeout
```

### Checklist 24h

- [ ] Loki mémoire stable < 1GB
- [ ] Aucun OOM kill de Loki
- [ ] Logs arrivent dans Grafana
- [ ] Requêtes Grafana < 2s
- [ ] Pas de crash worker Gunicorn
- [ ] Backend stable (logs normaux)

---

## ⚠️ Rollback Plan

### Si Problème Immédiat

```bash
# Revenir au commit précédent
git revert HEAD
git push origin master

# Redeploy
./deploy.sh

# Ou restore du backup
tar -xzf backup-configs-*.tar.gz -C /app/AmbianceBoard
docker compose -f docker-compose.prod.yml restart loki promtail
```

### Si Loki Crash (OOM)

```bash
# Augmenter la limite mémoire
vim docker-compose.prod.yml
# Changer : limits: memory: 1g → 2g

# Redeploy
docker compose -f docker-compose.prod.yml up -d loki

# Vérifier
docker stats loki
```

### Si Logs Perdus

```bash
# Augmenter le rate limit
vim loki-config.yml
# Changer : ingestion_rate_mb: 10 → 20

# Redeploy
docker compose -f docker-compose.prod.yml restart loki
```

---

## 🎯 Expected Results

### Mémoire Loki

**Avant** : Croissance infinie → OOM après 1-2 jours
**Après** : Stable à 512MB-800MB

### Utilisation CPU

**Avant** : Pics élevés lors de charges
**Après** : < 50% (limité à 1 CPU)

### Performance Requêtes

**Avant** : Timeouts HTTP, lenteur
**Après** : < 1 seconde

### Logs Accumulation

**Avant** : ∞ (disque plein après X jours)
**Après** : Auto-cleanup après 7 jours

### Worker Gunicorn

**Avant** : Timeout crashes fréquents
**Après** : Stable, pas de timeouts

---

## 🆘 Quick Support

### Si Deployment Échoue

1. Vérifier la syntaxe YAML :
   ```bash
   docker run --rm -v $(pwd):/w grafana/loki:latest \
     -config.file=/w/loki-config.yml -log.level=error
   ```

2. Vérifier les logs :
   ```bash
   docker logs loki
   docker logs promtail
   ```

3. Vérifier l'espace disque :
   ```bash
   df -h /var/lib/docker/volumes
   ```

### Contacts

- Backend issues : Voir les logs Gunicorn
- Loki issues : Voir `LOKI_STABILITY_FIX.md`
- Timeout issues : Voir `FINAL_TIMEOUT_FIX.md`

---

## 📚 Documentation Référence

| Document | Contenu |
|----------|---------|
| `LOKI_STABILITY_FIX.md` | Problèmes identifiés + solutions détaillées |
| `LOKI_FIX_SUMMARY.md` | Résumé + troubleshooting complet |
| `FINAL_TIMEOUT_FIX.md` | Fix du timeout Gunicorn (non-blocking) |
| `GUNICORN_TIMEOUT_FIX.md` | Archive - première tentative |

---

## ✅ Deployment Successful When

- [ ] Loki mémoire < 1GB (stable)
- [ ] Backend sans timeout CRITICAL/ERROR
- [ ] Logs arrivent dans Grafana
- [ ] Requêtes Loki < 1s
- [ ] Tous containers "Up"
- [ ] 24h d'uptime sans redémarrage

---

**Ready to Deploy?**

```bash
git push origin master
./deploy.sh
# Then run: ./verify-deployment.sh  # (créer ce script si besoin)
```

---

**Estimated Deployment Time**: 10-15 minutes
**Expected Downtime**: < 1 minute (juste le redémarrage des containers)

