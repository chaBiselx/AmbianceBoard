import Cookie from '@/modules/Cookie';
import ModalCustom from '@/modules/Modal';

type playlist = { color: string, colorText: string, typePlaylist: string };

simulatePlaylistColor();
toggleShowColorForm();
toggleShowDelayForm();

const DomElementAddEvent = ['id_name', 'id_color', 'id_colorText', 'id_icon', 'id_typePlaylist', 'id_useSpecificColor'];
for (const element of DomElementAddEvent) {
    const input = document.getElementById(element) as HTMLInputElement
    if (input) {
        input.addEventListener('input', simulatePlaylistColor);
        input.addEventListener('change', simulatePlaylistColor);
    }
}


document.addEventListener("DOMContentLoaded", () => {
    const volumeInput = document.getElementById('id_volume') as HTMLInputElement;
    setVolumeToAllMusic(parseFloat(volumeInput.value));
    volumeInput.addEventListener('change', eventChangeVolume);
    const id_useSpecificColor = document.getElementById('id_useSpecificColor');
    if (id_useSpecificColor) {
        id_useSpecificColor.addEventListener('change', toggleShowColorForm);
    }
    const id_useSpecificDelay = document.getElementById('id_useSpecificDelay');
    if (id_useSpecificDelay) {
        id_useSpecificDelay.addEventListener('change', toggleShowDelayForm);
    }
    addMusicEvent();
    addDeletePlaylistEvent();
    addDeleteMusicEvent();
    addPopupDescriptionPlaylistType();
    addListingOtherColorsEvent();
});

function simulatePlaylistColor() {
    const demo = document.getElementById('demo-playlist') as HTMLDivElement;
    const id_useSpecificColor = document.getElementById('id_useSpecificColor') as HTMLInputElement;
    if (demo == null) {
        return
    }

    if (id_useSpecificColor?.checked) {
        const color = document.getElementById('id_color') as HTMLInputElement;
        const colorText = document.getElementById('id_colorText') as HTMLInputElement;
        demo.style.backgroundColor = color.value;
        demo.style.color = colorText.value;
    } else {
        const id_typePlaylist = document.getElementById('id_typePlaylist') as HTMLInputElement;
        if (id_typePlaylist) {
            const color = document.getElementById(`default_${id_typePlaylist.value}_color`) as HTMLInputElement;
            const colorText = document.getElementById(`default_${id_typePlaylist.value}_colorText`) as HTMLInputElement;
            demo.style.backgroundColor = color.value;
            demo.style.color = colorText.value;
        }
    }

    const imgInput = document.getElementById('id_icon') as HTMLInputElement;
    if (imgInput.value != "") {
        const reader = new FileReader();
        reader.addEventListener("load", () => {
            demo.innerHTML = "<img class='playlist-img' src=" + reader.result + " ></img>";
        });
        if (imgInput.files?.[0]) {
            reader.readAsDataURL(imgInput.files[0])
        }

    } else if (document.getElementById('id_icon_alreadyexist')) {
        const urlImg = document.getElementById('id_icon_alreadyexist') as HTMLLinkElement;
        demo.innerHTML = "<img class='playlist-img' src=" + urlImg.href + " ></img>";
    } else {
        const inputName = document.getElementById('id_name') as HTMLInputElement;
        demo.textContent = inputName.value;
    }

}




function eventChangeVolume(event: Event) {
    const volumeInput = event.target as HTMLInputElement;
    setVolumeToAllMusic(parseFloat(volumeInput.value));
}

function setVolumeToAllMusic(volume: number) {
    const listMusic = document.querySelectorAll('.music-player');
    listMusic.forEach((el) => {
        const music = el as HTMLAudioElement;
        music.volume = volume / 100;
    });
}

function toggleShowColorForm() {
    const listClass = document.getElementsByClassName('color_form')
    const id_useSpecificColor = document.getElementById('id_useSpecificColor') as HTMLInputElement;
    if (id_useSpecificColor?.checked) {
        for (const classElement of listClass) {
            classElement.classList.remove('d-none');
        }
    } else {
        for (const classElement of listClass) {
            classElement.classList.add('d-none');
        }
    }
}

function toggleShowDelayForm() {
    const listClass = document.getElementsByClassName('delay_form')
    const id_useSpecificDelay = document.getElementById('id_useSpecificDelay') as HTMLInputElement;
    if (id_useSpecificDelay?.checked) {
        for (const classElement of listClass) {
            classElement.classList.remove('d-none');
        }
    } else {
        for (const classElement of listClass) {
            classElement.classList.add('d-none');
        }
    }

}

function addDeletePlaylistEvent() {
    const deletePlaylistBtn = document.getElementById('btn-delete-playlist');
    if (deletePlaylistBtn) {
        deletePlaylistBtn.addEventListener('click', confirmSuppressionPlaylist);
    }
}


function confirmSuppressionPlaylist(event: Event) {
    const el = event.target as HTMLButtonElement;
    if (el.dataset.deleteurl && el.dataset.redirecturl) {
        const config = {
            delete_url: el.dataset.deleteurl,
            redirect_url: el.dataset.redirecturl,
        };

        if (confirm("Êtes-vous sûr de vouloir supprimer la playlist ?")) {
            deleteEntity(config)
        } else {
            // Annuler la suppression
        }

    }
}

function deleteEntity(config: { delete_url: string, redirect_url: string }) {
    fetch(config.delete_url, {
        method: 'DELETE',
        headers: {
            'X-CSRFToken': Cookie.get('csrftoken')!
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

function addDeleteMusicEvent() {
    const deleteMusicBtnList = document.getElementsByClassName('btn-delete-music');
    for (const deleteMusicBtn of deleteMusicBtnList) {
        deleteMusicBtn.addEventListener('click', confirmSuppressionMusic);
    }

}


function confirmSuppressionMusic(event: Event) {
    const el = event.target as HTMLButtonElement;
    if (el.dataset.deleteurl && el.dataset.redirecturl) {
        const config = {
            delete_url: el.dataset.deleteurl,
            redirect_url: el.dataset.redirecturl,
        };

        if (confirm("Êtes-vous sûr de vouloir supprimer la musique ?")) {
            deleteEntity(config)
        } else {
            // Annuler la suppression
        }

    }
}

function addPopupDescriptionPlaylistType() {
    const typePlaylistDescriptionBtn = document.getElementById('btn-show-description-playlist-type');
    if (typePlaylistDescriptionBtn) {
        typePlaylistDescriptionBtn.addEventListener('click', showDescriptionType);
    }
}

function showDescriptionType(e: Event) {
    const element = e.target as HTMLButtonElement;
    const url = element.dataset.url!;
    const title = "Selectionner Couleur existantes";

    fetch(url, {
        method: 'GET',
    })
        .then(response => response.text())
        .then((body) => {
            ModalCustom.show({
                title: title,
                body: body,
                footer: "",
                width: "lg"
            })
        })
        .catch(error => {
            console.error('Erreur lors de la requête AJAX:', error);
        });
}

function addListingOtherColorsEvent() {
    const el = document.getElementById('btn-select-other-color');
    if (el) {
        el.addEventListener('click', getListingOtherColors);
    }
}

function getListingOtherColors(event: Event) {
    const el = event.target as HTMLElement;
    const url = el.dataset.url!;
    const title = "Selectionner Couleur existantes";

    fetch(url, {
        method: 'GET',
    })
        .then(response => response.json())
        .then((body) => {
            const divRow = document.createElement("div") as HTMLElement;
            divRow.classList.add("row");

            if (body.default_playlists) {
                const title = document.createElement("h3")
                title.classList.add("text-center");
                title.innerHTML = "Playlist Defauts"
                divRow.appendChild(title);
                body.default_playlists.forEach(el => {
                    const playlist = el as playlist;
                    appendChildPlaylist(divRow, playlist)
                })
            }
            if (body.unique_playlists) {
                divRow.appendChild(document.createElement("hr"));
                const title = document.createElement("h3")
                title.classList.add("text-center");
                title.innerHTML = "Playlist Uniques"
                divRow.appendChild(title);
                body.default_playlists.forEach(el => {
                    const playlist = el as playlist;
                    appendChildPlaylist(divRow, playlist)
                })
            }
            ModalCustom.show({
                title: title,
                body: divRow.outerHTML,
                footer: "",
                width: "lg"
            })

            const btnSelectPlaylistColorList = document.getElementsByClassName("btn-select-playlist-color");
            for (const btnSelectPlaylistColor of btnSelectPlaylistColorList) {
                btnSelectPlaylistColor.addEventListener('click', selectColor);
            }
        })
        .catch(error => {
            console.error('Erreur lors de la requête AJAX:', error);
        });
}

function appendChildPlaylist(divRow: HTMLElement, playlist: playlist) {
    const divCol1 = document.createElement("div");
    divCol1.classList.add("col-4")
    const divElement = document.createElement("div");
    divElement.innerHTML = "<small>Lorem</small>";
    divElement.style.backgroundColor = playlist.color;
    divElement.style.color = playlist.colorText;
    divElement.classList.add("playlist-element");
    divElement.classList.add("playlist-dim-75");
    divElement.classList.add("m-1")

    const divCol2 = document.createElement("div");
    divCol2.classList.add("col-5")
    divCol2.innerHTML = `<small>${playlist.typePlaylist}</small>`;

    const divCol3 = document.createElement("div");
    divCol3.classList.add("col-3")

    const button = document.createElement("button");
    button.classList.add("btn");
    button.classList.add("btn-primary");
    button.classList.add("btn-select-playlist-color");
    button.type = "button";
    button.title = "choisir cette couleur";
    button.textContent = "choisir";
    button.dataset.color = playlist.color;
    button.dataset.colorText = playlist.colorText;

    divCol3.appendChild(button);
    divCol1.appendChild(divElement);
    divRow.appendChild(divCol1);
    divRow.appendChild(divCol2);
    divRow.appendChild(divCol3);

}

function selectColor(event: Event) {
    console.log("selectColor");

    const el = event.target as HTMLButtonElement;
    const color = el.dataset.color!;
    const colorText = el.dataset.colorText!;
    const id_colorText = document.getElementById("id_colorText") as HTMLInputElement;
    const id_color = document.getElementById("id_color") as HTMLInputElement;
    if (id_colorText && id_color) {
        id_color.value = color;
        id_colorText.value = colorText;
    }
    ModalCustom.hide();
    simulatePlaylistColor();
}

function addMusicEvent() {
    const addMusicBtnList = document.getElementsByClassName('btn-add-music');
    if (addMusicBtnList) {
        for (const addMusicBtn of addMusicBtnList) {
            addMusicBtn.addEventListener('click', showPopupMusic);
        }
    }
}

function showPopupMusic(event: Event) {
    const el = event.target as HTMLButtonElement;;
    const url = el.dataset.url!;
    const title = el.title;

    fetch(url, {
        method: 'GET',
    })
        .then(response => response.text())
        .then((body) => {
            ModalCustom.show({
                title: title,
                body: body,
                footer: "",
                width: "lg"
            })
            const fileInput = document.getElementById('id_file');
            if (fileInput) {
                fileInput.addEventListener('change', autoSetAlternateName);
            }

        })
        .catch(error => {
            console.error('Erreur lors de la requête AJAX:', error);
        });
}

function autoSetAlternateName(event: Event) {
    const fileInputOrigin = event.target as HTMLInputElement;
    const fileDest = document.getElementById('id_alternativeName') as HTMLInputElement;
    if (fileDest && fileInputOrigin && fileDest.value == '') {
        const regexExtenstion = /\.[^.]*$/g;
        if (fileInputOrigin.files?.[0]) {
            fileDest.value = fileInputOrigin.files[0].name.replace(regexExtenstion, '').substring(0, 50);
        }
    }

}