
import Config from '@/modules/General/Config';
import Csrf from "@/modules/General/Csrf";
import Cookie from '@/modules/General/Cookie';

import { ButtonPlaylist } from '@/modules/ButtonPlaylist';
import { MixerManager } from '@/modules/MixerManager';
import { SoundBoardManager } from '@/modules/SoundBoardManager';
import WakeLock from '@/modules/General/WakeLock';
import ModalCustom from './modules/General/Modal';
import SharedSoundBoardWebSocket from '@/modules/SharedSoundBoardWebSocket';
import SharedSoundBoardUtil from '@/modules/SharedSoundBoardUtil';
import { MixerPlaylist } from "@/modules/MixerPlaylist";
import ShareLinkManager from '@/modules/Event/ShareLinkManager';
import ConsoleTesteur from '@/modules/General/ConsoleTesteur';


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
            'X-CSRFToken': Csrf.getToken()!
        }
    }).then(response => response.text()).then((body) => {
        ModalCustom.show({
            title: "Lien partage",
            body: body,
            footer: "",
            width: "sm"
        });
        (new ShareLinkManager()).addEvent();
        const WebSocketUrl = Cookie.get('WebSocketUrl');
        if (WebSocketUrl && !SharedSoundBoardUtil.isSlavePage()) {
            SharedSoundBoardWebSocket.setNewInstance(atob(WebSocketUrl), true);
            ConsoleTesteur.log("WebSocket Master call from publishSoundboard");
            const sharedSoundBoardWebSocket = (SharedSoundBoardWebSocket.getMasterInstance());
            sharedSoundBoardWebSocket.start();
        }
    })

}

function showPopupSharedPlaylist() {
    const activeWS = SharedSoundBoardUtil.isSlavePage()
    if (activeWS) {
        const button = document.createElement("button");
        button.id = "btn-start-websocket";
        button.classList.add("btn", "btn-primary", "btn-block");
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
    const url = SharedSoundBoardUtil.getSlaveUrl()
    if (url) {

        (SharedSoundBoardWebSocket.getSlaveInstance(url)).start();


    }

}


