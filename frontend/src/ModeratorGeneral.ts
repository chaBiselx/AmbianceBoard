import ModalCustom from '@/modules/Modal';

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

class FetchPopupData {
    url: string
    title: string
    constructor(url: string, title: string) {
        this.url = url;
        this.title = title
    }

    public fetch() {
        console.log('fetch');
        
        fetch(this.url, {
            method: 'GET',
        })
            .then(response => response.text())
            .then((body) => {
               this.show(body)
            })
            .catch(error => {
                console.error('Erreur lors de la requête AJAX:', error);
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
}

