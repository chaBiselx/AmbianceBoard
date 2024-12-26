const ID_DIV_PLAYER = 'players';
const DEBUG = true;
const TRUE = 'True';//TODO fix type soundboard_read
const FALSE = 'False';

document.addEventListener("DOMContentLoaded", (event) => {
    addEventListenerDom()
});


function addEventListenerDom() {
    const formElements = document.querySelectorAll('.playlist-link');

    formElements.forEach(element => {
        element.addEventListener('click', eventTogglePlaylist);
    });
}

function eventTogglePlaylist(event) {
    const dataset = event.target.dataset;
    addPlaylist(dataset);
}

function addPlaylist(dataset) {
    console.log(dataset);

    const audioElement = document.getElementById(`playlist-audio-${dataset.playlistId}`);
    console.log(audioElement);

    if (!audioElement) {
        deleteSameTypePlaylist(dataset);
        audio = createPlaylistLink(dataset);
        audio.addEventListener('ended', () => {
            audio.remove();
            if (dataset.playlistLoop == TRUE) {
                addPlaylist(dataset);
            }
        });
    } else {
        audioElement.remove();
    }

}

function createPlaylistLink(dataset) {
    if (DEBUG) console.log('createPlaylistLink');

    const audioElementDiv = document.getElementById(ID_DIV_PLAYER);
    const audio = document.createElement('audio');
    audio.id = `playlist-audio-${dataset.playlistId}`;
    audio.src = dataset.playlistUri;
    audio.volume = dataset.playlistVolume / 100;
    audio.autoplay = true;
    audio.classList.add('audio-' + dataset.playlistType);
    audioElementDiv.appendChild(audio);
    audio.addEventListener('error', function (event) {
        console.log(event.target.error)
        if (event.target.error.code === 4) { // => ERROR 404
            createClientNotification({ message: 'Aucune musique n\'est presente dans cette playlist', type: 'error', duration: 2000 });
        }
    });
    audio.play();
    return audio
}

function deleteSameTypePlaylist(dataset) {
    if (DEBUG) console.log('deleteSameTypePlaylist');
    if (DEBUG) console.log(dataset.playlistSingleconcurrentread);
    if (dataset.playlistSingleconcurrentread == TRUE) {
        const audioElementDiv = document.getElementById(ID_DIV_PLAYER);
        const audio = audioElementDiv.getElementsByClassName('audio-' + dataset.playlistType);
        if (DEBUG) console.log('audio-' + dataset.playlistType);
        for (let audioDom of audio) {
            if (DEBUG) console.log('remove');
            if (DEBUG) console.log(audioDom);

            audioDom.remove();
        }
    }
}