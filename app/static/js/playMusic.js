const ID_DIV_PLAYER = 'players';
const DEBUG = true;
const TRUE = 'True';//TODO fix type soundboard_read
const FALSE = 'False';
const INTERVAL_FADE = 50;

class FadeStrategy {
    calculateVolume(startVolume, endVolume, progress) {
        throw new Error("Méthode calculateVolume doit être implémentée");
    }
}

class LinearFade extends FadeStrategy {
    calculateVolume(startVolume, endVolume, progress) {
        return startVolume + (endVolume - startVolume) * progress;
    }
}

class EaseFade extends FadeStrategy {
    calculateVolume(startVolume, endVolume, progress) {
        return startVolume + (endVolume - startVolume) * (progress < 0.5 ? 2 * progress * progress : 1 - Math.pow(-2 * progress + 2, 2) / 2);
    }
}

class EaseInFade extends FadeStrategy {
    calculateVolume(startVolume, endVolume, progress) {
        return startVolume + (endVolume - startVolume) * Math.pow(progress, 2);
    }
}

class EaseOutFade extends FadeStrategy {
    calculateVolume(startVolume, endVolume, progress) {
        return startVolume + (endVolume - startVolume) * (1 - Math.pow(1 - progress, 2));
    }
}

function selectTypeFade(fadeType) {
    switch (fadeType) {
        case 'linear':
            return new LinearFade();
        case 'ease':
            return new EaseFade();
        case 'ease-in':
            return new EaseInFade();
        case 'ease-out':
            return new EaseOutFade();
        default:
            return new LinearFade();
    }
}

class AudioFadeManager {
    constructor(audioElement, fadeStrategy = new LinearFade(), isFadeIn = true, onComplete) {
        this.audioElement = audioElement;
        this.fadeStrategy = fadeStrategy;
        this.isFadeIn = isFadeIn;
        this.onComplete = onComplete;
        this.duration = 1000; // Durée par défaut de 1 seconde
        this.interval = 100; // Intervalle de mise à jour en millisecondes

        this.startVolume = this.isFadeIn ? 0 : 1;
        this.endVolume = this.isFadeIn ? 1 : 0;

        this.audioElement.dataset.levelFade = this.startVolume;
        updateVolumeElement(this.audioElement);
    }

    setDuration(durationInSec) {
        this.duration = durationInSec * 1000;
    }

    setFadeStrategy(fadeStrategy) {
        this.fadeStrategy = fadeStrategy;
    }

    start() {
        let currentTime = 0;
        const intervalId = setInterval(() => {
            currentTime += this.interval;
            const progress = currentTime / this.duration;

            const volume = this.fadeStrategy.calculateVolume(this.startVolume, this.endVolume , progress);
            this.audioElement.dataset.levelFade = volume;

            if (currentTime >= this.duration) {
                this.audioElement.dataset.levelFade = this.endVolume ;
                clearInterval(intervalId);
                if (this.onComplete) {
                    this.onComplete();
                }
            }
            updateVolumeElement(this.audioElement);
        }, this.interval);
    }
}

document.addEventListener("DOMContentLoaded", (event) => {
    addEventListenerDom()
    listMixer = document.getElementsByClassName('mixer-playlist');
    for (let mixer of listMixer) {
        mixer.addEventListener('change', eventChangeVolume);
    };
    if (DEBUG) {
        document.getElementById('players').style.display = 'block';
    }

});

function eventChangeVolume(event) {
    mixer = event.target
    if (mixer.id == 'mixer-general') {
        listType = document.getElementsByClassName('mixer-playlist-type')
        for (let typeMixer of listType) {
            changeSpecifiqueVolume(typeMixer.dataset.type);
        }

    } else {
        changeSpecifiqueVolume(mixer.dataset.type);
    }

}

function changeSpecifiqueVolume(type) {
    listAudio = document.getElementsByClassName('audio-' + type);
    for (let audio of listAudio) {
        updateVolumeElement(audio)
    };
}


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
    let audioElement = document.getElementsByClassName(`playlist-audio-${dataset.playlistId}`);
    if (audioElement.length == 0) {
        deleteSameTypePlaylist(dataset);
        createPlaylistLink(dataset);

    } else {
        removeClassActivePlaylist(dataset.playlistId);
        while (audioElement.length > 0) { // delete all playlist
            audioElement[0].remove();
        }
    }

}

function createPlaylistLink(dataset) {
    if (DEBUG) console.log('createPlaylistLink', dataset);

    const audioElementDiv = document.getElementById(ID_DIV_PLAYER);
    const audio = document.createElement('audio');
    audio.className = `playlist-audio-${dataset.playlistId}`;
    audio.src = dataset.playlistUri + "?i=" + Date.now(); // cache busting
    audio.autoplay = true;
    audio.dataset.idplaylist = dataset.playlistId;
    audio.dataset.defaultVolume = dataset.playlistVolume / 100;
    audio.dataset.playlistType = dataset.playlistType;
    audio.dataset.fadeintype = dataset.playlistFadeintype;
    audio.dataset.fadeouttype = dataset.playlistFadeouttype;
    audio.dataset.levelFade = 1;
    if (DEBUG) {
        audio.controls = true;
    }
    updateVolumeElement(audio)

    audio.classList.add('audio-' + dataset.playlistType);
    audioElementDiv.appendChild(audio);
    audio.addEventListener('error', function (event) {
        if (event.target.error.code === 4) { // => ERROR 404
            removeClassActivePlaylist(dataset.playlistId);
            createClientNotification({ message: 'Aucune musique n\'est presente dans cette playlist', type: 'danger', duration: 2000 });
            event.target.remove();
        }
    });
    if (dataset.playlistFadein == TRUE) {
        addFadeIn(audio, dataset)
    }
    if (dataset.playlistFadeout == TRUE) {

        audio.addEventListener('ended', () => {
            audio.remove();
        });
        audio.addEventListener('loadedmetadata', () => {
            audio.addEventListener('timeupdate', eventFadeOut);
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
    // console.log(`timeRemaining: ${timeRemaining} seconds / playlistFadeoutduration : ${dataset.playlistFadeoutduration}`); // timeRemaining);
    // console.log(parseFloat(timeRemaining) <= dataset.playlistFadeoutduration); // timeRemaining);
    // console.log(audio.dataset.fadeOut); // timeRemaining);

    if (parseFloat(timeRemaining) <= dataset.playlistFadeoutduration && audio.dataset.fadeOut != true) {

        audio.removeEventListener('timeupdate', eventFadeOut);
        addFadeOut(audio, dataset);
        if (dataset.playlistLoop == TRUE) {
            if (DEBUG) console.log("eventFadeOut loop");
            createPlaylistLink(dataset); // don't use addPlaylist => delete  fade out 
        } else {
            removeClassActivePlaylist(dataset.playlistId);
        }
    }
}


function addFadeIn(audio, dataset) {
    if (DEBUG) console.log('addFadeIn');
    audio.dataset.levelFade = 0;
    audio.dataset.fadeIn = true

    typeFade = selectTypeFade(audio.dataset.fadeintype)
    audioFade = new AudioFadeManager(audio, typeFade, true, () => {
        audio.dataset.levelFade = 1;
        delete audio.dataset.fadeIn;
    });
    audioFade.setDuration(dataset.playlistFadeinduration)

    audio.addEventListener('playing', () => {
        time = Date.now();
        while(audio.readyState != 2) {
            if(time + 2000 < Date.now()) {
                break;
            }
        }
        audioFade.start();
    })

}

function addFadeOut(audio, dataset) {
    if (DEBUG) console.log('addFadeOut');
    if (audio.dataset.fadeIn) {
        if (DEBUG) console.log('ignore fade out if fade in not finished');
        return // ignore fade out if fade in not finished
    }

    typeFade = selectTypeFade(audio.dataset.fadeouttype)
    audioFade = new AudioFadeManager(audio, typeFade, false, () => {
        audio.dataset.levelFade = 1;
        delete audio.dataset.fadeIn;
    });
    audioFade.setDuration(dataset.playlistFadeinduration)
    audioFade.start();
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

function updateVolumeElement(audioDom) {
    VolumeDefault = audioDom.dataset.defaultVolume
    VolumeFade = audioDom.dataset.levelFade
    VolumeMixerGeneral = getVolumeMixerGeneral()
    VolumeMixerType = getVolumeMixerType(audioDom.dataset.playlistType)
    // console.log(`VolumeDefault: ${VolumeDefault} VolumeFade: ${VolumeFade} VolumeMixerGeneral: ${VolumeMixerGeneral} VolumeMixerType: ${VolumeMixerType}`);
    // console.log(VolumeDefault * VolumeFade * VolumeMixerGeneral * VolumeMixerType);

    audioDom.volume = Math.min(1, Math.max(0, VolumeDefault * VolumeFade * VolumeMixerGeneral * VolumeMixerType))

}

function getVolumeMixerGeneral() {
    return document.getElementById('mixer-general').value;
}

function getVolumeMixerType(type) {
    return document.getElementById(`mixer-${type}`).value;
}
