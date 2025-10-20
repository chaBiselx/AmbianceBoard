import ModalCustom from '@/modules/General/Modal';
import ConsoleCustom from "@/modules/General/ConsoleCustom";

document.addEventListener('DOMContentLoaded', () => {
    for (const el of document.querySelectorAll('.popup-data-playlist')) {
        el.addEventListener('click', getDataPlaylist);
    }
    for (const el of document.querySelectorAll('.popup-data-soundboard'))    {
        el.addEventListener('click', getDataSoundboard);
    }
    for (const el of document.querySelectorAll('.popup-data-user')) {
        el.addEventListener('click', getDataUser);
    }
    for (const el of document.querySelectorAll('.popup-add-tag')) {
        el.addEventListener('click', getAddtag);
    }
    for (const el of document.querySelectorAll('.popup-info-tag')) {
        el.addEventListener('click', getInfoTag);
    }
    for (const el of document.querySelectorAll('.popup-edit-tag')) {
        el.addEventListener('click', getEditTag);
    }

})


function getDataPlaylist(event: Event) {
    const el = event.target as HTMLButtonElement;
    const url = el.dataset.url!;
    const title = "Playlist" + el.dataset.title;

    new FetchPopupData(url, title).fetch();
}

function getDataSoundboard(event: Event) {
    const el = event.target as HTMLButtonElement;
    const url = el.dataset.url!;
    const title = " Soundboard : " + el.dataset.title;

    new FetchPopupData(url, title).fetch();
}

function getDataUser(event: Event) {
    const el = event.target as HTMLButtonElement;
    const url = el.dataset.url!;
    const title = " log : " + el.dataset.title;

    new FetchPopupData(url, title).fetch();
}

function getAddtag(event: Event) {
    const el = event.target as HTMLButtonElement;
    const url = el.dataset.url!;
    const title = "Ajouter un tag"; 
    new FetchPopupData(url, title).fetch();
}

function getInfoTag(event: Event) {
    const el = event.target as HTMLButtonElement;
    const url = el.dataset.url!;
    const title = "Informations du tag";

    new FetchPopupData(url, title).fetch();
}

function getEditTag(event: Event) {

    const el = event.target as HTMLButtonElement;
    const url = el.dataset.url!;
    const title = "Modifier le tag";

    new FetchPopupData(url, title).fetch();
}

class FetchPopupData {
    url: string
    title: string
    constructor(url: string, title: string) {
        this.url = url;
        this.title = title
    }

    public fetch() {
        fetch(this.url, {
            method: 'GET',
        })
            .then(response => response.text())
            .then((body) => {
                this.show(body)
                this.setValue()
            })
            .catch(error => {
                ConsoleCustom.error('Erreur lors de la requête AJAX:', error);
            });
    }

    public show(body: string) {
        ModalCustom.show({
            title: this.title,
            body: body,
            footer: "",
            width: "lg"
        })
    }

    public setValue() {
        const currentPath = globalThis.location.pathname + globalThis.location.search;
        const redirectInput = document.getElementById('redirect_uri') as HTMLInputElement;
        if (redirectInput) {
            redirectInput.value = currentPath;
        }
    }
}

