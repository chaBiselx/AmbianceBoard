const ID_DIV_PLAYER = 'players';
const DEBUG = true;
const TRUE = 'True';//TODO fix type soundboard_read
const FALSE = 'False';
const INTERVAL_FADE = 50;

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
    addClassActivePlaylist(dataset.playlistId);
    addPlaylist(dataset);
}

function addPlaylist(dataset) {

    const audioElement = document.getElementById(`playlist-audio-${dataset.playlistId}`);

    if (!audioElement) {
        deleteSameTypePlaylist(dataset);
        createPlaylistLink(dataset);

    } else {
        removeClassActivePlaylist(dataset.playlistId);
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
    audio.dataset.idplaylist = dataset.playlistId;
    audio.classList.add('audio-' + dataset.playlistType);
    audioElementDiv.appendChild(audio);
    audio.addEventListener('error', function (event) {
        if (event.target.error.code === 4) { // => ERROR 404
            createClientNotification({ message: 'Aucune musique n\'est presente dans cette playlist', type: 'error', duration: 2000 });
        }
    });
    if (dataset.playlistFadein == TRUE) {
        addFadeIn(audio, dataset)
        setTimeout(() => {
            addFadeOut(audio, dataset)
        }, 2000)
    }
    if (dataset.playlistFadeout == TRUE) {

        audio.addEventListener('ended', () => {
            audio.remove();
        });
        audio.addEventListener('loadedmetadata', () => {

            if (dataset.playlistLoop == TRUE) {
                audio.addEventListener('timeupdate', eventFadeOut);
            }
        });
    } else {
        audio.addEventListener('ended', () => {
            audio.remove();
            if (dataset.playlistLoop == TRUE) {
                addPlaylist(dataset);
            } else {
                removeClassActivePlaylist(dataset.playlistId);
            }
        });
    }
    audio.play();
    return audio
}

function eventFadeOut(event) {
    audio = event.target
    dataset = document.getElementById(`playlist-${audio.dataset.idplaylist}`).dataset;


    const timeRemaining = audio.duration - audio.currentTime;

    if (timeRemaining <= dataset.playlistFadeoutduration) {
        audio.removeEventListener('timeupdate', eventFadeOut);
        addFadeOut(audio, dataset);
        if (dataset.playlistLoop == TRUE) {
            if (DEBUG) console.log("loop");
            createPlaylistLink(dataset); // don't use addPlaylist => delete  fade out 
        } else {
            removeClassActivePlaylist(dataset.playlistId);
        }
    }
}


function addFadeIn(audio, dataset) {
    if (DEBUG) console.log('addFadeIn');
    const volumeDest = dataset.playlistVolume / 100
    audio.volume = 0;
    audio.dataset.fadeIn = true

    audio.addEventListener('play', () => {
        const fadeInDuration = dataset.playlistFadeinduration * 1000;
        const step = volumeDest * (INTERVAL_FADE / fadeInDuration);

        const fadeIn = setInterval(() => {
            if (audio.volume < volumeDest) {
                audio.volume = Math.min(audio.volume + step, volumeDest);
            } else {
                delete audio.dataset.fadeIn
                clearInterval(fadeIn);
            }
        }, INTERVAL_FADE);
    })

}

function addFadeOut(audio, dataset) {
    if (DEBUG) console.log('addFadeOut');
    if (audio.dataset.fadeIn) {
        if (DEBUG) console.log('ignore fade out if fade in not finished');
        return // ignore fade out if fade in not finished
    }
    const volumeDest = dataset.playlistVolume / 100
    const fadeOutDuration = dataset.playlistFadeoutduration * 1000;
    const step = volumeDest * (INTERVAL_FADE / fadeOutDuration);

    const fadeOut = setInterval(() => {
        if (audio.volume > 0) {
            audio.volume = Math.max(audio.volume - step, 0);
        } else {
            clearInterval(fadeOut);
            audio.remove();
        }
    }, INTERVAL_FADE);
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
            removeClassActivePlaylist(audioDom.dataset.idplaylist);

            audioDom.remove();
        }
    }
}

function addClassActivePlaylist(idPlaylist) {
    document.getElementById(`playlist-${idPlaylist}`).classList.add("active-playlist")

}

function removeClassActivePlaylist(idPlaylist) {
    document.getElementById(`playlist-${idPlaylist}`).classList.remove("active-playlist")

}