import ModalCustom from '@/modules/General/Modal';
import ConsoleCustom from "@/modules/General/ConsoleCustom";

document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.popup-data-playlist').forEach((el) => {
        el.addEventListener('click', getDataPlaylist);
    })
    document.querySelectorAll('.popup-data-soundboard').forEach((el) => {
        el.addEventListener('click', getDataSoundboard);
    })
    document.querySelectorAll('.popup-data-user').forEach((el) => {
        el.addEventListener('click', getDataUser);
    })
        document.querySelectorAll('.popup-add-tag').forEach((el) => {
        el.addEventListener('click', getAddtag);
    })
    document.querySelectorAll('.popup-info-tag').forEach((el) => {
        el.addEventListener('click', getInfoTag);
    })
    document.querySelectorAll('.popup-edit-tag').forEach((el) => {
        el.addEventListener('click', getEditTag);
    })

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
        const currentPath = window.location.pathname + window.location.search;
        const redirectInput = document.getElementById('redirect_uri') as HTMLInputElement;
        if (redirectInput) {
            redirectInput.value = currentPath;
        }
    }
}

