
import Config from '@/modules/General/Config';
import Csrf from "@/modules/General/Csrf";
import Cookie from '@/modules/General/Cookie';

import { ButtonPlaylistFinder } from '@/modules/ButtonPlaylist';
import { MixerManager } from '@/modules/MixerManager';
import WakeLock from '@/modules/General/WakeLock';
import ModalCustom from '@/modules/General/Modal';
import SharedSoundBoardWebSocket from '@/modules/SharedSoundBoardWebSocket';
import SharedSoundBoardUtil from '@/modules/SharedSoundBoardUtil';
import ShareLinkManager from '@/modules/Event/ShareLinkManager';
import ConsoleTesteur from '@/modules/General/ConsoleTesteur';
import ConsoleCustom from "@/modules/General/ConsoleCustom";
import { SharedSoundboardCustomVolumeFactory } from '@/modules/SharedSoundboardCustomVolume';
import ShorcutKeyBoardDetector from "@/modules/Control/ShorcutKeyBoardDetector";
import SoundBoardEventListener from '@/modules/SoundBoardEventListener';
import StreamConnectionWarmup from '@/modules/StreamConnectionWarmup';
import SoundboardEditMode from '@/modules/SoundBoardEditor/SoundboardEditMode';




document.addEventListener("DOMContentLoaded", () => {
    // Why: reduire la latence percue du premier clic playlist.
    // How: prechauffe DNS/TCP/TLS vers l'origine de stream via StreamConnectionWarmup.
    new StreamConnectionWarmup().initialize();
    showPopupSharedPlaylist();
    new SoundBoardEventListener().addEventListenerDom();
    MixerManager.setUpMixerPlaylist();
    MixerManager.updatePlaylistVolumeWidths();
    addEventPublishEvent();
    new MixerManager().initializeEventListeners();
    if (Config.DEBUG) {
        const audioElementDiv = document.getElementById(Config.SOUNDBOARD_DIV_ID_PLAYERS);
        if (audioElementDiv) audioElementDiv.style.display = 'block';
    }
    // Activer le Wake Lock au chargement de la page
    new WakeLock().start();
    const sh = SharedSoundboardCustomVolumeFactory.create('shared-custom-volume-button', 'template-shared-volume');
    if (sh) {
        sh.addEvent();
    }
    new ShortcutKeyboardSoundboard().addEvent();
    new SoundboardEditMode().addEvent();

    // Initialiser automatiquement le WebSocket si on est en mode master
    initializeWebSocketIfMaster();
});




/**
 * Initializes WebSocket connection automatically for master pages.
 * Checks for WebSocketUrl cookie and starts connection if present and not in slave mode.
 * @returns {void}
 */
function initializeWebSocketIfMaster(): void {
    const WebSocketUrl = Cookie.get('WebSocketUrl');
    if (WebSocketUrl && !SharedSoundBoardUtil.isSlavePage()) {
        try {
            SharedSoundBoardWebSocket.setNewInstance(atob(WebSocketUrl), true);
            ConsoleTesteur.log("WebSocket Master auto-initialized on page load");
            SharedSoundBoardWebSocket.getMasterInstance();
        } catch (error) {
            ConsoleCustom.error("Error auto-initializing WebSocket:", error);
        }
    }
}

/**
 * Attaches a click event listener to the publish soundboard button.
 * @returns {void}
 */
function addEventPublishEvent() {
    const button = document.getElementById(`btn-publish-soundboard`);
    if (button) {
        button.addEventListener('click', publishSoundboard);
    }
}

/**
 * Displays the sharing link modal for the soundboard.
 * @param {Event} event - The click event that triggered the publish action
 * @returns {void}
 */
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
        // Le WebSocket est déjà initialisé au chargement, pas besoin de le recréer
    })

}

/**
 * Displays the shared playlist popup if the page is in slave mode.
 * @returns {void}
 */
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


/**
 * Activates the WebSocket connection for slave playlist synchronization.
 * @returns {void}
 */
function activeWebSocket() {
    ModalCustom.hide();
    const url = SharedSoundBoardUtil.getSlaveUrl()
    if (url) {

        (SharedSoundBoardWebSocket.getSlaveInstance(url)).start();


    }

}

/**
 * Manages keyboard shortcuts for controlling soundboard playlists.
 */
class ShortcutKeyboardSoundboard {
    shortcutElementsSection: HTMLElement | null;
    ShorcutKeyBoardDetector: ShorcutKeyBoardDetector;
    recoardedShortcuts: Map<string, string> = new Map();
    /**
     * Creates a new keyboard shortcut manager instance.
     */
    constructor() {
        this.shortcutElementsSection = document.getElementById('list-shortcut-keyboard');
        this.ShorcutKeyBoardDetector = new ShorcutKeyBoardDetector();
    }

    /**
     * Registers all keyboard shortcuts and starts listening for keyboard input.
     * @returns {void}
     */
    public addEvent() {
        if (this.shortcutElementsSection) {
            const shortcutElements = this.shortcutElementsSection.getElementsByClassName('shortcut-element');
            for (const element of shortcutElements) {
                if (!(element instanceof HTMLElement)) continue;
                const shortCut = element.dataset.shortcut;
                const uuidPlaylist = element.dataset.playlistUuid;
                if (shortCut && uuidPlaylist) {
                    this.registerShortcut(shortCut, uuidPlaylist);
                }

            }
        }

        this.ShorcutKeyBoardDetector.startListening(
            (shortcut: string[]) => {
                const shortcutString = shortcut.join('##');
                const uuidPlaylist = this.recoardedShortcuts.get(shortcutString);
                if (uuidPlaylist) {
                    ConsoleCustom.log("Shortcut detected:", shortcutString, "-> Playlist UUID:", uuidPlaylist);
                    const button = ButtonPlaylistFinder.search(uuidPlaylist);
                    button?.simulateClick();
                    return false;
                } else {
                    ConsoleCustom.log("Shortcut detected but no playlist registered:", shortcutString);
                    return true;
                }
            }
        );


    }

    /**
     * Registers a keyboard shortcut to trigger a specific playlist.
     * @param {string} shortcut - The keyboard shortcut combination
     * @param {string} uuidPlaylist - The UUID of the playlist to trigger
     * @returns {void}
     */
    public registerShortcut(shortcut: string, uuidPlaylist: string) {
        this.recoardedShortcuts.set(shortcut, uuidPlaylist);
    }
}


