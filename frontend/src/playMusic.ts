

import Config from './modules/Config';

import { ButtonPlaylist} from './modules/ButtonPlaylist';
import { MixerManager } from './modules/MixerManager';
import { SoundBoardManager } from './modules/SoundBoardManager';


document.addEventListener("DOMContentLoaded", () => {
    addEventListenerDom()
    new MixerManager().initializeEventListeners();
    if (Config.DEBUG) {
        const audioElementDiv = document.getElementById(Config.SOUNDBOARD_DIV_ID_PLAYERS);
        if (audioElementDiv) audioElementDiv.style.display = 'block';
    }

});

function addEventListenerDom() {
    const formElements = document.querySelectorAll('.playlist-link');
    formElements.forEach(element => {
        element.addEventListener('click', eventTogglePlaylist);
    });
}

function eventTogglePlaylist(event: Event) {
    if (event.target instanceof HTMLElement) {
        const buttonPlaylist = new ButtonPlaylist(event.target)
        buttonPlaylist.active();
        SoundBoardManager.addPlaylist(buttonPlaylist);
    }

}




