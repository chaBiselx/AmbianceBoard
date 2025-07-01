

import Config from '@/modules/Config';

import { ButtonPlaylist } from '@/modules/ButtonPlaylist';
import { MixerManager } from '@/modules/MixerManager';
import { SoundBoardManager } from '@/modules/SoundBoardManager';
import WakeLock from '@/modules/WakeLock';
import ModalCustom from './modules/Modal';
import Cookie from '@/modules/Cookie';
import SharedSoundBoardWebSocket from '@/modules/SharedSoundBoardWebSocket';
import {MixerPlaylist} from "@/modules/MixerPlaylist";


document.addEventListener("DOMContentLoaded", () => {
    showPopupSharedPlaylist();
    addEventListenerDom()
    addEventListenerPlaylistVolumeUpdate();
    addEventShowHidePlayslitMixer();
    updateWithMixerPlaylist();
    addEventPublishEvent();
    new MixerManager().initializeEventListeners();
    if (Config.DEBUG) {
        const audioElementDiv = document.getElementById(Config.SOUNDBOARD_DIV_ID_PLAYERS);
        if (audioElementDiv) audioElementDiv.style.display = 'block';
    }
    // Activer le Wake Lock au chargement de la page
    new WakeLock().start();

});

function addEventShowHidePlayslitMixer(): void {
    const inputShowMixerPlaylist = document.getElementById('inputShowMixerPlaylist');
    if (inputShowMixerPlaylist) {
        inputShowMixerPlaylist.addEventListener('change', togglePlaylistMixer);
    }
}

function addEventListenerDom() {
    const formElements = document.querySelectorAll('.playlist-link');
    formElements.forEach(element => {
        if (element.classList.contains('disabled')) return
        element.addEventListener('click', eventTogglePlaylist);
    });
}

function togglePlaylistMixer() {
    const listMixerUpdate = document.getElementsByClassName('mixer-playlist-update-container');
    const checkBox = document.getElementById('inputShowMixerPlaylist') as HTMLInputElement
    document.getElementById('inputShowMixerPlaylist-show')?.classList.toggle('d-none')
    document.getElementById('inputShowMixerPlaylist-hide')?.classList.toggle('d-none')
    const showMixer = checkBox.checked
    if (listMixerUpdate) {
        for (const mixerUpdate of listMixerUpdate) {
            if (showMixer) {
                mixerUpdate.classList.remove('hide-playlist-mixer');
            } else {
                mixerUpdate.classList.add('hide-playlist-mixer');
            }
        }
    }
}

function addEventListenerPlaylistVolumeUpdate() {
    const mixerPlaylist = new MixerPlaylist();
    mixerPlaylist.addEventListener();
}



function eventTogglePlaylist(event: Event) {
    if (event.target instanceof HTMLElement) {
        const buttonPlaylist = new ButtonPlaylist(event.target)
        if (!buttonPlaylist.isActive()) {
            buttonPlaylist.active();
            SoundBoardManager.addPlaylist(buttonPlaylist);
        } else {
            buttonPlaylist.disactive();
            SoundBoardManager.removePlaylist(buttonPlaylist);

        }
    }
}

function updateWithMixerPlaylist() {
    const formElements = document.getElementsByClassName(`playlist-link`) as HTMLCollectionOf<HTMLAudioElement>;
    for (const element of formElements) {
        const elmentDest = document.getElementById(`range_volume_${element.dataset.playlistId!}`)
        if (elmentDest) {
            elmentDest.style.width = `${element.offsetWidth}px`;
        }
    }
}

function addEventPublishEvent() {
    const button = document.getElementById(`btn-publish-soundboard`);
    if (button) {
        button.addEventListener('click', publishSoundboard);
    }
}

function publishSoundboard(event: Event) {

    const button = event.target as HTMLButtonElement;
    const url = button.dataset.url as string;

    fetch(url, {
        method: 'GET',
        headers: {
            'X-CSRFToken': Cookie.get('csrftoken')!
        }
    }).then(response => response.text()).then((body) => {
        ModalCustom.show({
            title: "Lien partage",
            body: body,
            footer: "",
            width: "sm"
        })
    })

}

function showPopupSharedPlaylist() {
    const activeWS = document.getElementById('active-WS')
    if (activeWS) {
        const button = document.createElement("button");
        button.id = "btn-start-websocket";
        button.classList.add("btn");
        button.classList.add("btn-primary");
        button.classList.add("btn-block");
        button.textContent = "Activer la playlist";
        document.getElementById('btn-shared-playlist')?.appendChild(button);

        ModalCustom.show({
            title: "Partage de playlist",
            body: button.outerHTML,
            footer: "",
            width: "sm",
            callback: () => {
                const buttonListener = document.getElementById(`btn-start-websocket`);
                if (buttonListener) {

                    buttonListener.addEventListener('click', activeWebSocket);
                }
            }
        })

    }
}


function activeWebSocket() {
    ModalCustom.hide();
    const activeWS = document.getElementById('active-WS')
    if (activeWS) {
        const url = activeWS.dataset.url
        if (!url) return

        (SharedSoundBoardWebSocket.getInstance(url)).start();


    }

}


