#!/usr/bin/env bash
# Recupere la base PostgreSQL et les mediafiles de production vers le homelab.
# Usage et configuration : infra/homelab/backup/README.md

set -Eeuo pipefail

# =============================================================================
# Variables
# =============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LIB_DIR="$SCRIPT_DIR/lib"

# Fichier de configuration optionnel, jamais versionne (voir backup.env.example).
ENV_FILE="${BACKUP_ENV_FILE:-$SCRIPT_DIR/../backup.env}"
if [[ -f "$ENV_FILE" ]]; then
    # shellcheck disable=SC1090
    source "$ENV_FILE"
fi

# Connexion au serveur
TRANSPORT="${TRANSPORT:-ssh}"
PROD_USER="${PROD_USER:-}"
PROD_HOST="${PROD_HOST:-}"
PROD_KEY="${PROD_KEY:-}"
PROD_BASE_PATH="${PROD_BASE_PATH:-}"

# Base de donnees
DB_SERVICE="${DB_SERVICE:-db}"
DB_USER="${DB_USER:-}"
DB_NAME="${DB_NAME:-}"
DB_EXCLUDE_TABLES="${DB_EXCLUDE_TABLES:-}"
LOCAL_BACKUPS="${LOCAL_BACKUPS:-}"
RETENTION_DAYS="${RETENTION_DAYS:-0}"

# Mediafiles
PROD_MEDIA="${PROD_MEDIA:-$PROD_BASE_PATH/mediafiles}"
LOCAL_MEDIA="${LOCAL_MEDIA:-}"

# Options de la ligne de commande
DO_DB=1
DO_MEDIA=1
DRY_RUN=0
MIRROR=0
VERIFY=0

# Execution
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
LOCK_FILE="${TMPDIR:-/tmp}/ambianceboard-backup.lock"
WORK_DIR=""

# =============================================================================
# Fonctions
# =============================================================================

source "$LIB_DIR/common.sh"
source "$LIB_DIR/backup-db.sh"
source "$LIB_DIR/backup-media.sh"

usage() {
    cat <<'USAGE'
Usage : backup-homelab.sh [options]

  --db-only      Sauvegarde uniquement la base
  --media-only   Sauvegarde uniquement les mediafiles
  --dry-run      Simulation : aucun fichier local ecrit
  --delete       Miroir exact des medias (supprime en local les fichiers absents de la prod)
  --verify       Compare les empreintes md5 des medias apres transfert
  -h, --help     Affiche cette aide
USAGE
}

parse_args() {
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --db-only) DO_MEDIA=0 ;;
            --media-only) DO_DB=0 ;;
            --dry-run) DRY_RUN=1 ;;
            --delete) MIRROR=1 ;;
            --verify) VERIFY=1 ;;
            -h | --help) usage; exit 0 ;;
            *) usage >&2; die "option inconnue : $1" ;;
        esac
        shift
    done

    if [[ "$DO_DB" -eq 0 && "$DO_MEDIA" -eq 0 ]]; then
        die "--db-only et --media-only sont incompatibles"
    fi
}

load_transport() {
    local transport_file="$LIB_DIR/transports/$TRANSPORT.sh"

    if [[ ! -f "$transport_file" ]]; then
        die "transport inconnu : $TRANSPORT (attendu : un fichier $transport_file)"
    fi

    # shellcheck disable=SC1090
    source "$transport_file"
}

check_config() {
    require_vars PROD_BASE_PATH

    if [[ ! "$RETENTION_DAYS" =~ ^[0-9]+$ ]]; then
        die "RETENTION_DAYS doit etre un entier"
    fi
}

# Empeche deux sauvegardes simultanees (ex. cron + lancement manuel).
acquire_lock() {
    exec 9>"$LOCK_FILE"

    if ! flock -n 9; then
        die "une sauvegarde est deja en cours ($LOCK_FILE)"
    fi
}

create_work_dir() {
    WORK_DIR="$(mktemp -d)"
    trap 'rm -rf "$WORK_DIR"' EXIT
}

# =============================================================================
# Execution
# =============================================================================

parse_args "$@"
check_config
require_commands flock
acquire_lock
create_work_dir

load_transport
log "Transport : $TRANSPORT"
transport_check

if [[ "$DRY_RUN" -eq 1 ]]; then
    log "Mode simulation : aucun fichier local ne sera ecrit"
fi

# Base puis medias, au plus pres dans le temps pour limiter les references orphelines.
if [[ "$DO_DB" -eq 1 ]]; then
    backup_db
fi

if [[ "$DO_MEDIA" -eq 1 ]]; then
    backup_media
fi

log "Sauvegarde terminee"
