#!/bin/bash
# LOKI STABILITY - Verification Script
# À exécuter après le déploiement pour vérifier que tout est OK

set -e

echo "🔍 LOKI STABILITY VERIFICATION"
echo "================================"
echo ""

# Fonction pour afficher le résultat
check() {
    if [ $? -eq 0 ]; then
        echo "✅ $1"
    else
        echo "❌ $1"
        exit 1
    fi
}

# 1. Vérifier que les containers démarrent
echo "1️⃣  Checking containers..."
docker compose -f docker-compose.prod.yml ps | grep -q "loki.*Up"
check "Loki container is running"

docker compose -f docker-compose.prod.yml ps | grep -q "promtail.*Up"
check "Promtail container is running"

# 2. Vérifier la mémoire Loki
echo ""
echo "2️⃣  Checking Loki memory..."
LOKI_MEM=$(docker stats loki --no-stream --format "{{.MemUsage}}" | grep -oE '[0-9.]+[MG]' | head -1 | sed 's/[MG]//')
echo "   Loki memory: ${LOKI_MEM}M"

# Convertir GB en MB si nécessaire
if [[ $LOKI_MEM == *"G"* ]]; then
    LOKI_MEM_NUM=$(echo $LOKI_MEM | sed 's/G//' | awk '{print $1 * 1024}')
else
    LOKI_MEM_NUM=$LOKI_MEM
fi

if (( $(echo "$LOKI_MEM_NUM < 1024" | bc -l) )); then
    check "Loki memory < 1GB"
else
    echo "❌ Loki memory > 1GB (should be < 1GB)"
    exit 1
fi

# 3. Vérifier que Loki répond
echo ""
echo "3️⃣  Checking Loki connectivity..."
curl -s http://localhost:3100/loki/api/v1/labels > /dev/null
check "Loki is responding to requests"

# 4. Vérifier les logs Loki
echo ""
echo "4️⃣  Checking Loki logs..."
docker logs loki --tail 50 | grep -q "listening"
check "Loki is listening on port 3100"

if docker logs loki --tail 50 | grep -qi "error\|panic\|cannot allocate"; then
    echo "❌ Found errors in Loki logs"
    docker logs loki --tail 20
    exit 1
else
    echo "✅ No critical errors in Loki logs"
fi

# 5. Vérifier Promtail
echo ""
echo "5️⃣  Checking Promtail..."
docker logs promtail --tail 20 | grep -q "scrape_configs"
check "Promtail configuration loaded"

if docker logs promtail --tail 50 | grep -qi "panic\|fatal"; then
    echo "❌ Found fatal errors in Promtail"
    docker logs promtail --tail 20
    exit 1
else
    echo "✅ Promtail running without fatal errors"
fi

# 6. Vérifier le backend
echo ""
echo "6️⃣  Checking Backend..."
docker logs back-1 --tail 50 | grep -q "Booting worker"
check "Backend worker is running"

if docker logs back-1 --tail 50 | grep -qi "CRITICAL.*TIMEOUT\|SIGKILL"; then
    echo "❌ Found timeout errors in backend"
    exit 1
else
    echo "✅ No timeout errors in backend"
fi

# 7. Résumé
echo ""
echo "================================"
echo "✅ ALL CHECKS PASSED!"
echo "================================"
echo ""
echo "📊 Summary:"
echo "   - Loki memory: ${LOKI_MEM}B (< 1GB) ✅"
echo "   - Loki responding: YES ✅"
echo "   - Promtail running: YES ✅"
echo "   - Backend stable: YES ✅"
echo ""
echo "🚀 Loki stability fix is successfully deployed!"
echo ""
echo "Next steps:"
echo "  1. Monitor for 24 hours: docker stats loki promtail"
echo "  2. Check Grafana Explore for logs"
echo "  3. Verify no OOM kills: docker inspect loki | grep OOMKilled"
echo ""
