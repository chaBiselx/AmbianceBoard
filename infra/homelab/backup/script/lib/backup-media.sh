# Sauvegarde des mediafiles (voir _procedure/BACKUP-MEDIAFILES.md).

show_remote_media_stats() {
    local size
    local count

    size=$(transport_exec "du -sh $PROD_MEDIA | cut -f1")
    count=$(transport_exec "find $PROD_MEDIA -type f | wc -l")
    log "Mediafiles en production : $size, $count fichier(s)"
}

sync_media() {
    local options=(-az --partial --human-readable --info=stats2,progress2)

    if [[ "$DRY_RUN" -eq 1 ]]; then
        options+=(--dry-run --verbose)
    fi

    if [[ "$MIRROR" -eq 1 ]]; then
        options+=(--delete)
    fi

    transport_sync "$PROD_MEDIA" "$LOCAL_MEDIA" "${options[@]}"
}

# Verifie que chaque fichier de prod est present a l'identique en local.
# Les fichiers locaux supplementaires (sans --delete) sont toleres.
verify_media() {
    local remote_sums="$WORK_DIR/remote.md5"
    local local_sums="$WORK_DIR/local.md5"
    local missing="$WORK_DIR/missing.md5"

    log "Verification des empreintes md5"
    transport_exec "cd $PROD_MEDIA && find . -type f -exec md5sum {} +" | sort > "$remote_sums"
    (cd "$LOCAL_MEDIA" && find . -type f -exec md5sum {} +) | sort > "$local_sums"

    comm -23 "$remote_sums" "$local_sums" > "$missing"

    if [[ -s "$missing" ]]; then
        log "Fichiers absents ou differents en local :"
        cat "$missing"
        die "verification des medias echouee"
    fi

    log "Verification OK : tous les fichiers de production sont identiques en local"
}

backup_media() {
    log "=== Mediafiles : $PROD_MEDIA ==="
    require_vars PROD_MEDIA LOCAL_MEDIA
    prepare_local_dir "$LOCAL_MEDIA"
    show_remote_media_stats

    sync_media

    if [[ "$DRY_RUN" -eq 1 ]]; then
        return
    fi

    log "Mediafiles en local : $(find "$LOCAL_MEDIA" -type f | wc -l) fichier(s)"

    if [[ "$VERIFY" -eq 1 ]]; then
        verify_media
    fi
}
