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
    togglePlaylist(dataset);
}

function togglePlaylist(dataset) {
    const audioElement = document.getElementById(`playlist-audio-${dataset.playlistId}`);
    if (!audioElement) {
        audio = createPlaylistLink(dataset);
        audio.addEventListener('ended', () => {
            audio.remove();
            togglePlaylist(dataset);
        });
    } else {
        audioElement.remove();
    }

}

function createPlaylistLink(dataset) {
    const audioElementDiv = document.getElementById(`players`);
    const audio = document.createElement('audio');
    audio.id = `playlist-audio-${dataset.playlistId}`;
    audio.src = dataset.playlistUri;
    audio.volume = dataset.playlistVolume / 100;
    audio.autoplay = true;
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