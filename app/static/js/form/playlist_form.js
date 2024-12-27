document.addEventListener("DOMContentLoaded", (event) => {
    volumeInput = document.getElementById('id_volume');
    setVolumeToAllMusic(volumeInput.value);
    volumeInput.addEventListener('change', eventChangeVolume);

});

function eventChangeVolume(event) {
    volume = event.target.value;
    setVolumeToAllMusic(volume);
}

function setVolumeToAllMusic(volume) {
    const listMusic = document.querySelectorAll('.music-player');
    listMusic.forEach((music) => {
        music.volume = volume / 100;
    });
}



function confirmSuppressionPlaylist(el) {
    config = {};
    config.delete_url = el.dataset.deleteurl;
    config.redirect_url = el.dataset.redirecturl;

    if (confirm("Êtes-vous sûr de vouloir supprimer cet élément ?")) {
        callAjaxDeletePlaylist(config)
    } else {
        // Annuler la suppression
    }
}

function callAjaxDeletePlaylist(config) {
    var csrfToken = getCookie('csrftoken');
    fetch(config.delete_url, {
        method: 'DELETE',
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


function confirmSuppressionMusic(el) {
    config = {};
    config.delete_url = el.dataset.deleteurl;
    config.redirect_url = el.dataset.redirecturl;

    if (confirm("Êtes-vous sûr de vouloir supprimer cet élément ?")) {
        callAjaxDeleteMusic(config)
    } else {
        // Annuler la suppression
    }
}

function callAjaxDeleteMusic(config) {
    var csrfToken = getCookie('csrftoken');
    fetch(config.delete_url, {
        method: 'DELETE',
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