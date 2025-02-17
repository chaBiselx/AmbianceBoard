function getDataPlaylist(el){
    const url = el.dataset.url;
    const title = "Playlist" + el.dataset.title;

    fetch(url, {
        method: 'GET',
    })
        .then(response => response.text())
        .then((body) => {
            modalShow({
                title: title,
                body: body,
                width: 'xl'
            })
            fileInput = document.getElementById('id_file');
            if (fileInput) {
                fileInput.addEventListener('change', autoSetAlternateName);
            }

        })
        .catch(error => {
            console.error('Erreur lors de la requête AJAX:', error);
        });
}

function getDataSoundboard(el){
    const url = el.dataset.url;
    const title = " Soundboard : " + el.dataset.title;

    fetch(url, {
        method: 'GET',
    })
        .then(response => response.text())
        .then((body) => {
            modalShow({
                title: title,
                body: body,
                width: 'xl'
            })
            fileInput = document.getElementById('id_file');
            if (fileInput) {
                fileInput.addEventListener('change', autoSetAlternateName);
            }

        })
        .catch(error => {
            console.error('Erreur lors de la requête AJAX:', error);
        });
}

function getDataUser(el){
    const url = el.dataset.url;
    const title = " log : " + el.dataset.title;

    fetch(url, {
        method: 'GET',
    })
        .then(response => response.text())
        .then((body) => {
            modalShow({
                title: title,
                body: body,
                width: 'xl'
            })
            fileInput = document.getElementById('id_file');
            if (fileInput) {
                fileInput.addEventListener('change', autoSetAlternateName);
            }

        })
        .catch(error => {
            console.error('Erreur lors de la requête AJAX:', error);
        });
}

