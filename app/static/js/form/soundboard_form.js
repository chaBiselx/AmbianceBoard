function confirmSuppression(config) {
    if (confirm("Êtes-vous sûr de vouloir supprimer cet élément ?")) {
        callAjax(config)
    } else {
        // Annuler la suppression
    }
}

function callAjax(config) {
    var csrfToken = getCookie('csrftoken');
    fetch(config.delete_url, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken
        },
    })
        .then(response => {
            if (response.status === 200) {
                window.location.href = config.redirect_url;
            } else {
                // Gestion des erreurs
                console.error('Erreur lors de la suppression');
            }
        })
        .catch(error => {
            console.error('Erreur lors de la requête AJAX:', error);
        });
}