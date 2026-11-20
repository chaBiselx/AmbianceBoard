# Fonctions utilitaires partagees par les scripts de sauvegarde.

log() {
    printf '[%s] %s\n' "$(date '+%F %T')" "$*"
}

die() {
    log "ERREUR : $*" >&2
    exit 1
}

# Verifie que chaque variable passee en argument est renseignee.
require_vars() {
    local var
    local missing=()

    for var in "$@"; do
        if [[ -z "${!var:-}" ]]; then
            missing+=("$var")
        fi
    done

    if [[ ${#missing[@]} -gt 0 ]]; then
        die "variables manquantes : ${missing[*]}"
    fi
}

require_commands() {
    local cmd

    for cmd in "$@"; do
        if ! command -v "$cmd" >/dev/null; then
            die "commande requise absente : $cmd"
        fi
    done
}

# Cree le dossier local s'il n'existe pas, avec un acces reserve au proprietaire.
prepare_local_dir() {
    local dir="$1"

    if [[ -d "$dir" ]]; then
        return
    fi

    if [[ "$DRY_RUN" -eq 1 ]]; then
        log "[simulation] creation du dossier $dir"
        return
    fi

    mkdir -p "$dir"
    chmod 700 "$dir"
}
