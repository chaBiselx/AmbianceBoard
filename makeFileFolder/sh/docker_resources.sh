#!/bin/bash

# Configuration
REFRESH_INTERVAL=${1:-2}  # Intervalle de rafraîchissement en secondes (défaut: 2s)
FILTER_NAME="ambianceboard"
HISTORY_FILE="./tmp/docker_stats_history.log"
MAX_HISTORY_LINES=1000

# Variables globales pour l'historique
declare -A cpu_history
declare -A mem_history
declare -A net_in_history
declare -A net_out_history
declare -A start_times

# Fonction pour initialiser l'historique
init_history() {
    if [ ! -f "$HISTORY_FILE" ]; then
        touch "$HISTORY_FILE"
        echo "Timestamp|Container|CPU|RAM|Net I/O" > "$HISTORY_FILE"
    fi
    
    # Limiter la taille du fichier d'historique
    if [ -f "$HISTORY_FILE" ] && [ $(wc -l < "$HISTORY_FILE") -gt $MAX_HISTORY_LINES ]; then
        tail -n $((MAX_HISTORY_LINES/2)) "$HISTORY_FILE" > "${HISTORY_FILE}.tmp"
        mv "${HISTORY_FILE}.tmp" "$HISTORY_FILE"
    fi
}

# Fonction pour enregistrer les métriques
log_metrics() {
    local container_name="$1"
    local cpu="$2"
    local mem="$3"
    local net_io="$4"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    echo "$timestamp|$container_name|$cpu|$mem|$net_io" >> "$HISTORY_FILE"
    
    # Mettre à jour les historiques en mémoire (dernières 10 valeurs)
    cpu_history["$container_name"]="${cpu_history["$container_name"]} $cpu"
    cpu_history["$container_name"]=$(echo "${cpu_history["$container_name"]}" | awk '{for(i=NF-9;i<=NF;i++) if(i>0) printf "%s ", $i}')
    
    mem_history["$container_name"]="${mem_history["$container_name"]} $mem"
    mem_history["$container_name"]=$(echo "${mem_history["$container_name"]}" | awk '{for(i=NF-9;i<=NF;i++) if(i>0) printf "%s ", $i}')
}

# Fonction pour calculer les moyennes
calculate_average() {
    local values="$1"
    if [ -z "$values" ]; then
        echo "0"
        return
    fi
    echo "$values" | awk '{sum=0; count=0; for(i=1;i<=NF;i++) {gsub(/%/,"",$i); if($i!="") {sum+=$i; count++}} if(count>0) print sum/count; else print 0}'
}

# Fonction pour obtenir les tendances
get_trend() {
    local values="$1"
    if [ -z "$values" ]; then
        echo "→"
        return
    fi
    
    local first=$(echo "$values" | awk '{gsub(/%/,"",$1); print $1}')
    local last=$(echo "$values" | awk '{gsub(/%/,"",$NF); print $NF}')
    
    if [ -z "$first" ] || [ -z "$last" ]; then
        echo "→"
    elif command -v bc &> /dev/null; then
        if [ $(echo "$last > $first + 5" | bc -l 2>/dev/null || echo 0) -eq 1 ]; then
            echo "📈"
        elif [ $(echo "$last < $first - 5" | bc -l 2>/dev/null || echo 0) -eq 1 ]; then
            echo "📉"
        else
            echo "→"
        fi
    else
        echo "→"
    fi
}

# Fonction pour nettoyer l'écran et afficher l'en-tête
show_header() {
    clear
    echo "=========================================================================="
    echo "           🐳 MONITORING DOCKER CONTAINERS - AmbianceBoard 🐳"
    echo "=========================================================================="
    echo "⏱️  Rafraîchissement: ${REFRESH_INTERVAL}s | 🛑 Ctrl+C pour quitter | 📊 Historique activé"
    echo "🕐 Timestamp: $(date '+%Y-%m-%d %H:%M:%S')"
    echo "=========================================================================="
    echo
}

# Fonction pour afficher les stats d'un conteneur avec historique
show_container_stats() {
    local container_id="$1"
    local container_name="$2"
    
    echo "┌──────────────────────────────────────────────────────────────────────────┐"
    echo "│ 📦 $container_name"
    echo "│ 🆔 ID: $container_id"
    
    # Obtenir les informations détaillées du conteneur
    local container_info=$(docker inspect "$container_id" --format '{{.State.StartedAt}}|{{.Config.Image}}|{{.State.Status}}|{{.RestartCount}}' 2>/dev/null)
    if [ -n "$container_info" ]; then
        local started_at=$(echo "$container_info" | cut -d'|' -f1 | cut -d'T' -f1)
        local image=$(echo "$container_info" | cut -d'|' -f2)
        local status=$(echo "$container_info" | cut -d'|' -f3)
        local restart_count=$(echo "$container_info" | cut -d'|' -f4)
        
        echo "│ 🖼️  Image: $image"
        echo "│ ▶️  Statut: $status | 🔄 Redémarrages: $restart_count"
        echo "│ 🚀 Démarré: $started_at"
    fi
    echo "└──────────────────────────────────────────────────────────────────────────┘"
    
    # Récupérer les stats actuelles
    local stats_output=$(docker stats "$container_id" --no-stream --format "{{.CPUPerc}}|{{.MemUsage}}|{{.MemPerc}}|{{.NetIO}}|{{.BlockIO}}|{{.PIDs}}" 2>/dev/null)
    if [ -n "$stats_output" ]; then
        local cpu=$(echo "$stats_output" | cut -d'|' -f1)
        local mem_usage=$(echo "$stats_output" | cut -d'|' -f2)
        local mem_perc=$(echo "$stats_output" | cut -d'|' -f3)
        local net_io=$(echo "$stats_output" | cut -d'|' -f4)
        local block_io=$(echo "$stats_output" | cut -d'|' -f5)
        local pids=$(echo "$stats_output" | cut -d'|' -f6)
        
        # Enregistrer dans l'historique
        log_metrics "$container_name" "$cpu" "$mem_perc" "$net_io"
        
        # Calculer les moyennes et tendances
        local cpu_avg=$(calculate_average "${cpu_history["$container_name"]}")
        local mem_avg=$(calculate_average "${mem_history["$container_name"]}")
        local cpu_trend=$(get_trend "${cpu_history["$container_name"]}")
        local mem_trend=$(get_trend "${mem_history["$container_name"]}")
        
        printf "  🖥️  CPU: %-8s (avg: %5.1f%%) %s
" "$cpu" "$cpu_avg" "$cpu_trend"
        printf "  🧠 RAM: %-15s (%s) (avg: %5.1f%%) %s
" "$mem_usage" "$mem_perc" "$mem_avg" "$mem_trend"
        printf "  🌐 Net I/O: %-20s
" "$net_io"
        printf "  💾 Block I/O: %-18s
" "$block_io"
        printf "  📊 PIDs: %-6s
" "$pids"
    else
        echo "  ❌ Impossible de récupérer les statistiques"
    fi
    echo
}

# Fonction pour afficher le résumé global avec historique
show_global_summary() {
    local containers="$1"
    local container_count=0
    if [ -n "$containers" ]; then
        container_count=$(echo "$containers" | wc -l)
    fi
    
    echo "┌──────────────────────────────────────────────────────────────────────────┐"
    echo "│ 📊 RÉSUMÉ GLOBAL DU SYSTÈME"
    echo "└──────────────────────────────────────────────────────────────────────────┘"
    
    # Statistiques Docker globales
    local total_containers=$(docker ps -q 2>/dev/null | wc -l)
    local total_images=$(docker images -q 2>/dev/null | wc -l)
    local docker_version=$(docker version --format '{{.Server.Version}}' 2>/dev/null || echo "N/A")
    
    echo "  🐳 Docker version: $docker_version"
    echo "  📦 Conteneurs AmbianceBoard actifs: $container_count"
    echo "  📦 Total conteneurs en cours: $total_containers"
    echo "  🖼️  Total images: $total_images"
    
    # Statistiques système si disponibles
    if command -v free &> /dev/null; then
        local mem_info=$(free -h 2>/dev/null | awk 'NR==2{printf "Utilisée: %s/%s (%s)", $3, $2, $5}')
        echo "  🧠 RAM système: $mem_info"
    fi
    
    if command -v df &> /dev/null; then
        local disk_info=$(df -h / 2>/dev/null | awk 'NR==2{printf "Utilisé: %s/%s (%s)", $3, $2, $5}')
        echo "  💾 Disque système: $disk_info"
    fi
    
    # Statistiques réseau Docker
    local network_count=$(docker network ls -q 2>/dev/null | wc -l)
    local volume_count=$(docker volume ls -q 2>/dev/null | wc -l)
    echo "  🌐 Réseaux Docker: $network_count"
    echo "  📁 Volumes Docker: $volume_count"
    
    # Historique récent (dernières 5 entrées)
    echo
    echo "  📈 HISTORIQUE RÉCENT (5 dernières mesures):"
    if [ -f "$HISTORY_FILE" ] && [ -s "$HISTORY_FILE" ]; then
        echo "     Timestamp            | Conteneur       | CPU    | RAM    | Net I/O"
        echo "     ──────────────────────┼─────────────────┼────────┼────────┼──────────"
        tail -n 5 "$HISTORY_FILE" 2>/dev/null | while IFS='|' read -r timestamp container cpu mem net; do
            if [ -n "$timestamp" ]; then
                printf "     %-20s | %-15s | %-6s | %-6s | %s
" "$timestamp" "$container" "$cpu" "$mem" "$net"
            fi
        done
    else
        echo "     Aucun historique disponible"
    fi
    
    echo
    echo "  🔄 Prochain rafraîchissement dans ${REFRESH_INTERVAL}s"
    echo "  📝 Historique stocké dans: $HISTORY_FILE"
    
    # Afficher les commandes utiles
    echo
    echo "  🛠️  COMMANDES UTILES:"
    echo "     ./docker_resources.sh 1    # Rafraîchissement chaque seconde"
    echo "     ./docker_resources.sh 5    # Rafraîchissement chaque 5 secondes"
    echo "     tail -f $HISTORY_FILE       # Suivre l'historique en temps réel"
    echo
}

# Fonction pour obtenir la liste des conteneurs une seule fois
get_containers() {
    docker ps --filter "name=$FILTER_NAME" --format "{{.ID}} {{.Names}}" 2>/dev/null
}

# Fonction de nettoyage à la sortie
cleanup() {
    echo
    echo "🛑 Arrêt du monitoring..."
    echo "📊 Historique sauvegardé dans: $HISTORY_FILE"
    exit 0
}

# Configurer le signal de sortie
trap cleanup SIGINT SIGTERM

# Vérifier si Docker est disponible
if ! command -v docker &> /dev/null; then
    echo "❌ Docker n'est pas installé ou pas accessible"
    exit 1
fi

# Vérifier que Docker daemon est en cours d'exécution
if ! docker info &> /dev/null; then
    echo "❌ Docker daemon n'est pas en cours d'exécution"
    exit 1
fi

# Boucle principale de monitoring
echo "🚀 Initialisation du monitoring Docker pour AmbianceBoard..."
init_history
echo "✅ Historique initialisé"
sleep 1

while true; do
    show_header
    
    # Obtenir la liste des conteneurs
    containers=$(get_containers)
    
    if [ -z "$containers" ]; then
        echo "❌ Aucun conteneur trouvé avec le filtre '$FILTER_NAME'"
        echo
        echo "📋 Conteneurs en cours d'exécution:"
        docker ps --format "   • {{.Names}} ({{.Image}}) - {{.Status}}" 2>/dev/null || echo "   Aucun conteneur en cours"
        echo
    else
        echo "$containers" | while IFS=' ' read -r container_id container_name; do
            if [ -n "$container_id" ] && [ -n "$container_name" ]; then
                show_container_stats "$container_id" "$container_name"
            fi
        done
    fi
    
    show_global_summary "$containers"
    
    # Attendre avant le prochain rafraîchissement
    sleep "$REFRESH_INTERVAL"
done

# Fonction pour enregistrer les métriques
log_metrics() {
    local container_name="$1"
    local cpu="$2"
    local mem="$3"
    local net_io="$4"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    echo "$timestamp|$container_name|$cpu|$mem|$net_io" >> "$HISTORY_FILE"
    
    # Mettre à jour les historiques en mémoire (dernières 10 valeurs)
    cpu_history["$container_name"]="${cpu_history["$container_name"]} $cpu"
    cpu_history["$container_name"]=$(echo "${cpu_history["$container_name"]}" | awk '{for(i=NF-9;i<=NF;i++) if(i>0) printf "%s ", $i}')
    
    mem_history["$container_name"]="${mem_history["$container_name"]} $mem"
    mem_history["$container_name"]=$(echo "${mem_history["$container_name"]}" | awk '{for(i=NF-9;i<=NF;i++) if(i>0) printf "%s ", $i}')
}

# Fonction pour calculer les moyennes
calculate_average() {
    local values="$1"
    if [ -z "$values" ]; then
        echo "0"
        return
    fi
    echo "$values" | awk '{sum=0; count=0; for(i=1;i<=NF;i++) {gsub(/%/,"",$i); if($i!="") {sum+=$i; count++}} if(count>0) print sum/count; else print 0}'
}

# Fonction pour obtenir les tendances
get_trend() {
    local values="$1"
    if [ -z "$values" ]; then
        echo "→"
        return
    fi
    
    local first=$(echo "$values" | awk '{gsub(/%/,"",$1); print $1}')
    local last=$(echo "$values" | awk '{gsub(/%/,"",$NF); print $NF}')
    
    if [ -z "$first" ] || [ -z "$last" ]; then
        echo "→"
    elif [ $(echo "$last > $first + 5" | bc -l 2>/dev/null || echo 0) -eq 1 ]; then
        echo "📈"
    elif [ $(echo "$last < $first - 5" | bc -l 2>/dev/null || echo 0) -eq 1 ]; then
        echo "📉"
    else
        echo "→"
    fi
}

# Fonction pour nettoyer l'écran et afficher l'en-tête
show_header() {
    clear
    echo "=========================================================================="
    echo "           🐳 MONITORING DOCKER CONTAINERS - AmbianceBoard 🐳"
    echo "=========================================================================="
    echo "⏱️  Rafraîchissement: ${REFRESH_INTERVAL}s | 🛑 Ctrl+C pour quitter | 📊 Historique activé"
    echo "🕐 Timestamp: $(date '+%Y-%m-%d %H:%M:%S')"
    echo "=========================================================================="
    echo
}

# Fonction pour afficher les stats d'un conteneur avec historique
show_container_stats() {
    local container_id="$1"
    local container_name="$2"
    
    echo "┌──────────────────────────────────────────────────────────────────────────┐"
    echo "│ 📦 $container_name"
    echo "│ 🆔 ID: $container_id"
    
    # Obtenir les informations détaillées du conteneur
    local container_info=$(docker inspect "$container_id" --format '{{.State.StartedAt}}|{{.Config.Image}}|{{.State.Status}}|{{.RestartCount}}')
    local started_at=$(echo "$container_info" | cut -d'|' -f1 | cut -d'T' -f1)
    local image=$(echo "$container_info" | cut -d'|' -f2)
    local status=$(echo "$container_info" | cut -d'|' -f3)
    local restart_count=$(echo "$container_info" | cut -d'|' -f4)
    
    echo "│ 🖼️  Image: $image"
    echo "│ ▶️  Statut: $status | 🔄 Redémarrages: $restart_count"
    echo "│ 🚀 Démarré: $started_at"
    echo "└──────────────────────────────────────────────────────────────────────────┘"
    
    # Récupérer les stats actuelles
    local stats_output=$(docker stats "$container_id" --no-stream --format "{{.CPUPerc}}|{{.MemUsage}}|{{.MemPerc}}|{{.NetIO}}|{{.BlockIO}}|{{.PIDs}}")
    local cpu=$(echo "$stats_output" | cut -d'|' -f1)
    local mem_usage=$(echo "$stats_output" | cut -d'|' -f2)
    local mem_perc=$(echo "$stats_output" | cut -d'|' -f3)
    local net_io=$(echo "$stats_output" | cut -d'|' -f4)
    local block_io=$(echo "$stats_output" | cut -d'|' -f5)
    local pids=$(echo "$stats_output" | cut -d'|' -f6)
    
    # Enregistrer dans l'historique
    log_metrics "$container_name" "$cpu" "$mem_perc" "$net_io"
    
    # Calculer les moyennes et tendances
    local cpu_avg=$(calculate_average "${cpu_history["$container_name"]}")
    local mem_avg=$(calculate_average "${mem_history["$container_name"]}")
    local cpu_trend=$(get_trend "${cpu_history["$container_name"]}")
    local mem_trend=$(get_trend "${mem_history["$container_name"]}")
    
    printf "  🖥️  CPU: %-8s (avg: %5.1f%%) %s\n" "$cpu" "$cpu_avg" "$cpu_trend"
    printf "  🧠 RAM: %-15s (%s) (avg: %5.1f%%) %s\n" "$mem_usage" "$mem_perc" "$mem_avg" "$mem_trend"
    printf "  🌐 Net I/O: %-20s\n" "$net_io"
    printf "  💾 Block I/O: %-18s\n" "$block_io"
    printf "  📊 PIDs: %-6s\n" "$pids"
    echo
}

# Fonction pour obtenir la liste des conteneurs une seule fois
get_containers() {
    docker ps --filter "name=$FILTER_NAME" --format "{{.ID}} {{.Names}}"
}

# Fonction de nettoyage à la sortie
cleanup() {
    echo
    echo "🛑 Arrêt du monitoring..."
    exit 0
}

# Configurer le signal de sortie
trap cleanup SIGINT SIGTERM

# Vérifier si Docker est disponible
if ! command -v docker &> /dev/null; then
    echo "❌ Docker n'est pas installé ou pas accessible"
    exit 1
fi

# Boucle principale de monitoring
while true; do
    show_header
    
    # Obtenir la liste des conteneurs
    containers=$(get_containers)
    
    if [ -z "$containers" ]; then
        echo "❌ Aucun conteneur trouvé avec le filtre '$FILTER_NAME'"
        echo "📋 Conteneurs en cours d'exécution:"
        docker ps --format "   • {{.Names}} ({{.Image}})"
    else
        echo "$containers" | while IFS=' ' read -r container_id container_name; do
            if [ -n "$container_id" ] && [ -n "$container_name" ]; then
                show_container_stats "$container_id" "$container_name"
            fi
        done
        
# Fonction pour afficher le résumé global avec historique
show_global_summary() {
    local containers="$1"
    local container_count=$(echo "$containers" | wc -l)
    
    echo "┌──────────────────────────────────────────────────────────────────────────┐"
    echo "│ 📊 RÉSUMÉ GLOBAL DU SYSTÈME"
    echo "└──────────────────────────────────────────────────────────────────────────┘"
    
    # Statistiques Docker globales
    local total_containers=$(docker ps -q | wc -l)
    local total_images=$(docker images -q | wc -l)
    local docker_version=$(docker version --format '{{.Server.Version}}' 2>/dev/null || echo "N/A")
    
    echo "  🐳 Docker version: $docker_version"
    echo "  📦 Conteneurs AmbianceBoard actifs: $container_count"
    echo "  📦 Total conteneurs en cours: $total_containers"
    echo "  🖼️  Total images: $total_images"
    
    # Statistiques système si disponibles
    if command -v free &> /dev/null; then
        local mem_info=$(free -h | awk 'NR==2{printf "Utilisée: %s/%s (%.1f%%)", $3, $2, $3*100/$2}')
        echo "  🧠 RAM système: $mem_info"
    fi
    
    if command -v df &> /dev/null; then
        local disk_info=$(df -h / | awk 'NR==2{printf "Utilisé: %s/%s (%s)", $3, $2, $5}')
        echo "  � Disque système: $disk_info"
    fi
    
    # Historique récent (dernières 5 entrées)
    echo
    echo "  📈 HISTORIQUE RÉCENT (5 dernières mesures):"
    if [ -f "$HISTORY_FILE" ]; then
        echo "     Timestamp            | Conteneur       | CPU    | RAM    | Net I/O"
        echo "     ──────────────────────┼─────────────────┼────────┼────────┼──────────"
        tail -n 5 "$HISTORY_FILE" | while IFS='|' read -r timestamp container cpu mem net; do
            printf "     %-20s | %-15s | %-6s | %-6s | %s\n" "$timestamp" "$container" "$cpu" "$mem" "$net"
        done
    else
        echo "     Aucun historique disponible"
    fi
    
    echo
    echo "  🔄 Prochain rafraîchissement dans ${REFRESH_INTERVAL}s"
    echo "  📝 Historique stocké dans: $HISTORY_FILE"
    echo
}
    fi
    
    # Attendre avant le prochain rafraîchissement
    sleep "$REFRESH_INTERVAL"
done