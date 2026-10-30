# Transport SSH : commandes via ssh, copie de dossiers via rsync sur ssh.
#
# Variables : PROD_USER, PROD_HOST, PROD_KEY.
# A travers un VPN, il suffit de renseigner PROD_HOST avec l'adresse du
# serveur dans le VPN : ce transport reste utilisable tel quel.
#
# Contrat a respecter par tout transport (lib/transports/<nom>.sh) :
#   transport_check                      verifie configuration et connexion
#   transport_exec "<commande>"          execute sur le serveur, stdout renvoye
#   transport_sync <dossier_distant> <dossier_local> [options rsync...]

SSH_OPTIONS="-i $PROD_KEY -o ServerAliveInterval=30 -o ServerAliveCountMax=4"

transport_check() {
    require_vars PROD_USER PROD_HOST PROD_KEY
    require_commands ssh rsync

    if [[ ! -r "$PROD_KEY" ]]; then
        die "cle SSH introuvable : $PROD_KEY"
    fi

    if ! transport_exec "true"; then
        die "connexion SSH impossible vers $PROD_HOST"
    fi
}

transport_exec() {
    local command="$1"

    # shellcheck disable=SC2086
    ssh $SSH_OPTIONS "$PROD_USER@$PROD_HOST" "$command"
}

transport_sync() {
    local remote_dir="$1"
    local local_dir="$2"
    shift 2

    # Le / final copie le contenu du dossier, pas le dossier lui-meme.
    rsync "$@" -e "ssh $SSH_OPTIONS" "$PROD_USER@$PROD_HOST:$remote_dir/" "$local_dir/"
}
