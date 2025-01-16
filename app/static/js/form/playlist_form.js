simulatePlaylistColor();

const DomElementAddEvent = ['id_name', 'id_color', 'id_colorText', 'id_icon'];
for (let i = 0; i < DomElementAddEvent.length; i++) {
    document.getElementById(DomElementAddEvent[i]).addEventListener('input', simulatePlaylistColor);
    document.getElementById(DomElementAddEvent[i]).addEventListener('change', simulatePlaylistColor);
}


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

function simulatePlaylistColor() {
    const demo = document.getElementById('demo-playlist')
    demo.style.backgroundColor = document.getElementById('id_color').value;
    demo.style.color = document.getElementById('id_colorText').value;

    if (document.getElementById('id_icon').value != "") {
        const reader = new FileReader();
        reader.addEventListener("load", () => {
            demo.innerHTML = "<img class='playlist-img' src=" + reader.result + " ></img>";
        });
        html =  reader.readAsDataURL(document.getElementById('id_icon').files[0]);
        if(html){
            demo.innerHTML = "<img class='playlist-img' src=" + html + " ></img>";
        }
    } else if(document.getElementById('id_icon_alreadyexist')){
        demo.innerHTML = "<img class='playlist-img' src=" + document.getElementById('id_icon_alreadyexist').href + " ></img>";
    } else {
        demo.textContent = document.getElementById('id_name').value;
    }

}

function showDescriptionType() {
    const div = document.createElement("div");
    const ul = document.createElement("ul");

    const li1 = document.createElement("li");
    li1.innerHTML = "Son instantanné";
    const li1Ul = document.createElement("ul");
    const li1Li1 = document.createElement("li");
    li1Li1.innerHTML = "choisi une musique aléatoire";
    const li1Li2 = document.createElement("li");
    li1Li2.innerHTML = "sans fade in/out";
    const li1Li3 = document.createElement("li");
    li1Li3.innerHTML = "sans lecture suivante";
    const li1Li4 = document.createElement("li");
    li1Li4.innerHTML = "peux etre jouer avec d'autre sons";
    li1Ul.appendChild(li1Li1);
    li1Ul.appendChild(li1Li2);
    li1Ul.appendChild(li1Li3);
    li1Ul.appendChild(li1Li4);
    li1.appendChild(li1Ul);

    const li2 = document.createElement("li");
    li2.innerHTML = "musique d'ambiences";
    const li2Ul = document.createElement("ul");
    const li2Li1 = document.createElement("li");
    li2Li1.innerHTML = "lit la playlist de musique de manière aléatoire";
    const li2Li2 = document.createElement("li");
    li2Li2.innerHTML = "avec fade in/out (3s)";
    const li2Li3 = document.createElement("li");
    li2Li3.innerHTML = "avec lecture suivante";
    const li2Li4 = document.createElement("li");
    li2Li4.innerHTML = "peux etre jouer avec d'autre sons";
    li2Ul.appendChild(li2Li1);
    li2Ul.appendChild(li2Li2);
    li2Ul.appendChild(li2Li3);
    li2Ul.appendChild(li2Li4);
    li2.appendChild(li2Ul);

    const li3 = document.createElement("li");
    li3.innerHTML = "musique de fond";
    const li3Ul = document.createElement("ul");
    const li3Li1 = document.createElement("li");
    li3Li1.innerHTML = "lit la playlist de musique de manière aléatoire";
    const li3Li2 = document.createElement("li");
    li3Li2.innerHTML = "avec fade in/out (5s)";
    const li3Li3 = document.createElement("li");
    li3Li3.innerHTML = "avec lecture suivante";
    const li3Li4 = document.createElement("li");
    li3Li4.innerHTML = "1 playlist de ce type musique par fois";
    li3Ul.appendChild(li3Li1);
    li3Ul.appendChild(li3Li2);
    li3Ul.appendChild(li3Li3);
    li3Ul.appendChild(li3Li4);
    li3.appendChild(li3Ul);

    ul.appendChild(li1);
    ul.appendChild(li2);
    ul.appendChild(li3);
    div.appendChild(ul);


    modalShow({
        title: 'Description',
        body: div.outerHTML,
        footer: '',
    });
}

function showPopupMusic(el) {
    const url = el.dataset.url;
    const title = el.title;

    fetch(url, {
        method: 'GET',
    })
        .then(response => response.text())
        .then((body) => {
            modalShow({
                title: title,
                body: body
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

function autoSetAlternateName(event) {
    fileDest = document.getElementById('id_alternativeName');
    if (fileDest && fileDest.value == '') {
        const regexExtenstion = /\.(.)*$/g;
        fileDest.value = event.target.files[0].name.replace(regexExtenstion, '').substring(0, 50);
    }

}