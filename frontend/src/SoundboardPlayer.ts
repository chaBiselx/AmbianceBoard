

import Config from './modules/Config';
import type {uri} from './type/General';

import { ButtonPlaylist, ButtonPlaylistFinder } from './modules/ButtonPlaylist';
import { MixerManager } from './modules/MixerManager';
import { SoundBoardManager } from './modules/SoundBoardManager';
import { UpdateVolumePlaylist } from './modules/UpdateVolumePlaylist';


document.addEventListener("DOMContentLoaded", () => {
    addEventListenerDom()
    addEventListenerPlaylistVolumeUpdate();
    addEventShowHidePlayslitMixer();
    updateWithMixerPlaylist();
    new MixerManager().initializeEventListeners();
    if (Config.DEBUG) {
        const audioElementDiv = document.getElementById(Config.SOUNDBOARD_DIV_ID_PLAYERS);
        if (audioElementDiv) audioElementDiv.style.display = 'block';
    }

});

function addEventShowHidePlayslitMixer() {
    const inputShowMixerPlaylist = document.getElementById('inputShowMixerPlaylist');
    if (inputShowMixerPlaylist) {
        inputShowMixerPlaylist.addEventListener('change', togglePlaylistMixer);
    }
}

function addEventListenerDom() {
    const formElements = document.querySelectorAll('.playlist-link');
    formElements.forEach(element => {
        element.addEventListener('click', eventTogglePlaylist);
    });
}

function togglePlaylistMixer() {
    const listMixerUpdate = document.getElementsByClassName('mixer-playlist-update-container');
    const checkBox = document.getElementById('inputShowMixerPlaylist') as HTMLInputElement
    const showMixer = checkBox.checked
    if (listMixerUpdate) {
        for (let i = 0; i < listMixerUpdate.length; i++) {
            if (showMixer) {
                listMixerUpdate[i].classList.remove('hide-playlist-mixer');
            } else {
                listMixerUpdate[i].classList.add('hide-playlist-mixer');
            }

        }
    }
}

function addEventListenerPlaylistVolumeUpdate() {
    const listMixerUpdate = document.getElementsByClassName('mixer-playlist-update');
    if (listMixerUpdate) {
        for (let i = 0; i < listMixerUpdate.length; i++) {
            listMixerUpdate[i].addEventListener('change', eventUpdatePlaylistVolume);
        }
    }

}

function eventUpdatePlaylistVolume(event: Event) {
    if (event.target instanceof HTMLInputElement) {
        if (event.target.dataset.idplaylist) {
            const buttonPlaylist = ButtonPlaylistFinder.search(event.target.dataset.idplaylist)
            if (buttonPlaylist) {
                let eventUpdateVolumePlaylist = new UpdateVolumePlaylist(buttonPlaylist, parseFloat(event.target.value));
                eventUpdateVolumePlaylist.updateVolume();
                
                const uri = event.target.dataset.playlistupdatevolumeuri as uri;
                eventUpdateVolumePlaylist.updateBackend(uri);
            }
        }
    }
}

function eventTogglePlaylist(event: Event) {
    if (event.target instanceof HTMLElement) {
        const buttonPlaylist = new ButtonPlaylist(event.target)
        buttonPlaylist.active();
        SoundBoardManager.addPlaylist(buttonPlaylist);
    }

}

function updateWithMixerPlaylist(){
    const formElements = document.querySelectorAll('.playlist-link');
    for (let index = 0; index < formElements.length; index++) {
        const element = formElements[index] as HTMLElement;
        const elmentDest = document.getElementById(`range_volume_${element.dataset.playlistId!}`)!
        elmentDest.style.width = `${element.offsetWidth}px`;
        
    }
}




