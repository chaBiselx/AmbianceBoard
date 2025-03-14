import ModalCustom from '@/modules/Modal.ts';

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


function getDataPlaylist(event:Event){
    const el = event.target as HTMLButtonElement;
    const url = el.dataset.url!;
    const title = "Playlist" + el.dataset.title;

    fetch(url, {
        method: 'GET',
    })
        .then(response => response.text())
        .then((body) => {
            ModalCustom.show({
                title: title,
                body: body,
                footer: "",
                width: 'xl'
            })
        })
        .catch(error => {
            console.error('Erreur lors de la requête AJAX:', error);
        });
}

function getDataSoundboard(event:Event){
    const el = event.target as HTMLButtonElement;
    const url = el.dataset.url;
    const title = " Soundboard : " + el.dataset.title;

    fetch(url, {
        method: 'GET',
    })
        .then(response => response.text())
        .then((body) => {
            ModalCustom.show({
                title: title,
                body: body,
                footer: "",
                width: 'xl'
            })
        })
        .catch(error => {
            console.error('Erreur lors de la requête AJAX:', error);
        });
}

function getDataUser(event:Event){
    const el = event.target as HTMLButtonElement;
    const url = el.dataset.url;
    const title = " log : " + el.dataset.title;

    fetch(url, {
        method: 'GET',
    })
        .then(response => response.text())
        .then((body) => {
            ModalCustom.show({
                title: title,
                body: body,
                footer: "",
                width: 'xl'
            })
        })
        .catch(error => {
            console.error('Erreur lors de la requête AJAX:', error);
        });
}

