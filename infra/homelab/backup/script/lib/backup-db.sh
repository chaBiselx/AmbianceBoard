# Sauvegarde de la base PostgreSQL (voir _procedure/BACKUP-BDD.md).

# Execute une commande dans le conteneur de la base, sur le serveur.
db_exec() {
    local command="$1"

    transport_exec "cd $PROD_BASE_PATH && docker compose -f docker-compose.prod.yml exec -T $DB_SERVICE $command"
}

show_db_size() {
    local size

    size=$(db_exec "psql -U $DB_USER -d $DB_NAME -tAc 'SELECT pg_size_pretty(pg_database_size(current_database()));'")
    log "Taille de la base : $size"
}

dump_db_to() {
    local target="$1"
    local exclude_options=""
    local table

    for table in $DB_EXCLUDE_TABLES; do
        exclude_options+=" --exclude-table=$table"
    done

    db_exec "pg_dump -U $DB_USER -F c$exclude_options $DB_NAME" > "$target"
}

# Renvoie un code d'erreur si le dump est inexploitable.
check_dump() {
    local dump_file="$1"

    if [[ ! -s "$dump_file" ]]; then
        log "Dump vide"
        return 1
    fi

    # Un dump au format custom commence toujours par la signature PGDMP.
    if [[ "$(head -c 5 "$dump_file")" != "PGDMP" ]]; then
        log "Signature PGDMP absente"
        return 1
    fi

    if ! command -v pg_restore >/dev/null; then
        log "pg_restore absent : verification limitee a la signature du dump"
        return 0
    fi

    if ! pg_restore --list "$dump_file" >/dev/null; then
        log "pg_restore --list a echoue"
        return 1
    fi

    log "Dump verifie avec pg_restore --list"
}

rotate_dumps() {
    if [[ "$RETENTION_DAYS" -eq 0 ]]; then
        return
    fi

    log "Suppression des dumps de plus de $RETENTION_DAYS jours"
    find "$LOCAL_BACKUPS" -maxdepth 1 -type f -name "${DB_NAME}_*.dump" \
        -mtime +"$RETENTION_DAYS" -print -delete
}

backup_db() {
    local target="$LOCAL_BACKUPS/${DB_NAME}_${TIMESTAMP}.dump"
    local partial="$target.partial"

    log "=== Base de donnees : $DB_NAME ==="
    require_vars PROD_BASE_PATH DB_SERVICE DB_USER DB_NAME LOCAL_BACKUPS
    prepare_local_dir "$LOCAL_BACKUPS"
    show_db_size

    if [[ "$DRY_RUN" -eq 1 ]]; then
        log "[simulation] dump vers $target"
        return
    fi

    # Le dump est ecrit sous un nom temporaire, renomme seulement s'il est valide.
    log "Dump en cours vers $target"
    if ! (umask 077 && dump_db_to "$partial") || ! check_dump "$partial"; then
        rm -f "$partial"
        die "dump invalide, fichier supprime"
    fi

    mv "$partial" "$target"
    log "Dump termine : $(du -h "$target" | cut -f1)"

    rotate_dumps
}
