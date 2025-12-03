
import Config from '@/modules/General/Config';
import Csrf from "@/modules/General/Csrf";
import Cookie from '@/modules/General/Cookie';

import { ButtonPlaylist, ButtonPlaylistFinder } from '@/modules/ButtonPlaylist';
import { MixerManager } from '@/modules/MixerManager';
import { SoundBoardManager } from '@/modules/SoundBoardManager';
import WakeLock from '@/modules/General/WakeLock';
import ModalCustom from '@/modules/General/Modal';
import SharedSoundBoardWebSocket from '@/modules/SharedSoundBoardWebSocket';
import SharedSoundBoardUtil from '@/modules/SharedSoundBoardUtil';
import { MixerPlaylist } from "@/modules/MixerPlaylist";
import ShareLinkManager from '@/modules/Event/ShareLinkManager';
import ConsoleTesteur from '@/modules/General/ConsoleTesteur';
import SharedSoundboardSendCmdMaster from '@/modules/SharedSoundboardSendCmdMaster';
import Time from '@/modules/Util/Time';
import { SharedSoundboardCustomVolumeFactory } from '@/modules/SharedSoundboardCustomVolume';
import ShorcutKeyBoardDetector from "@/modules/Control/ShorcutKeyBoardDetector";
import ConsoleCustom from "./modules/General/ConsoleCustom";
import { MusicDropzoneConfig, MusicDropzoneManager } from '@/modules/MusicDropzoneManager';
import Notification from '@/modules/General/Notifications';




document.addEventListener("DOMContentLoaded", () => {
    showPopupSharedPlaylist();
    addEventListenerDom()
    setUpMixerPlaylist();
    updateWithMixerPlaylist();
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
    new PopupAddMusicToSoundboard().showIfValue();
});

class PopupAddMusicToSoundboard {

    shortcutElementsInput: HTMLInputElement | null;

    constructor() {
        this.shortcutElementsInput = document.getElementById('new-playlist-uuid-popup') as HTMLInputElement | null;
    }

    public showIfValue() {
        if (this.shortcutElementsInput) {
            const uuidPlaylist = this.shortcutElementsInput.value;
            const url = this.shortcutElementsInput.dataset.url;

            if (uuidPlaylist && url) {
                fetch(url, {
                    method: 'GET',
                    headers: {
                        'X-CSRFToken': Csrf.getToken()!
                    }
                }).then(response => response.text()).then((body) => {
                    ModalCustom.show({
                        title: "Playlist ajoutée",
                        body: body,
                        footer: "",
                        width: "md",
                        callback: () => {
                            // TODO créer un class pour gérer cela 
                            const dropZone = document.getElementById('music-dropzone');
                            if (dropZone) {
                                const uploadUrl = dropZone.dataset.uploadUrl;
                                const csrf = Csrf.getToken();


                                if (!uploadUrl) {
                                    ConsoleCustom.error('Missing required configuration for MusicDropzoneManager');
                                    return;
                                }

                                try {
                                    (globalThis as typeof globalThis & { musicDropzoneManager?: MusicDropzoneManager }).musicDropzoneManager = new MusicDropzoneManager(
                                        {
                                            containerSelector: '#music-dropzone',
                                            uploadUrl: uploadUrl,
                                            csrf: csrf,
                                            fileFormat: dropZone.dataset.format,
                                            nbfile: Number.parseInt(dropZone.dataset.musicremaining!),
                                            refreshAfterUpload: false,
                                        } as MusicDropzoneConfig);
                                } catch (error) {
                                    ConsoleCustom.error('Error initializing MusicDropzoneManager:', error);
                                }
                            }

                            const sectionAction = document.getElementById('selection-type-ajout');
                            const sectionAddFile = document.getElementById('form-add-music-from-soundboard');
                            const sectionAddLink = document.getElementById('form-add-link-from-soundboard');
                            if (sectionAction && sectionAddFile && sectionAddLink) {
                                const addMusicFile = document.getElementById('btn-add-music-from-soundboard');
                                if (addMusicFile) {
                                    addMusicFile.addEventListener('click', () => {
                                        sectionAction.classList.add('d-none');
                                        sectionAddFile.classList.remove('d-none');
                                    });
                                }
                                const addMusicLink = document.getElementById('btn-add-link-from-soundboard');
                                if (addMusicLink) {
                                    addMusicLink.addEventListener('click', () => {
                                        sectionAction.classList.add('d-none');
                                        sectionAddLink.classList.remove('d-none');
                                    });
                                }

                                const form = document.getElementById('form-add-link-music-ajax');
                                const submitBtn = document.getElementById('submit-add-link-ajax') as HTMLButtonElement | null;
                                if (submitBtn && form instanceof HTMLFormElement) {
                                    submitBtn.addEventListener('click', function (e) {
                                        e.preventDefault();


                                        const formData = new FormData(form);
                                        const url = form.action;
                                        const submitBtn = form.querySelector('button[type="submit"]') as HTMLButtonElement | null;

                                        // Désactiver le bouton pendant l'envoi
                                        if (submitBtn) {
                                            submitBtn.disabled = true;
                                            submitBtn.textContent = 'Envoi en cours...';
                                        }

                                        fetch(url, {
                                            method: 'POST',
                                            body: formData,
                                            headers: {
                                                'X-Requested-With': 'XMLHttpRequest'
                                            }
                                        })
                                            .then(response => response.json())
                                            .then(data => {
                                                if (data.success) {
                                                    Notification.createClientNotification({ message: data.message, type: 'success' });
                                                    const bsModal = ModalCustom.getInstance();
                                                    if (bsModal) bsModal.hide();
                                                } else {
                                                    Notification.createClientNotification({ message: 'Une erreur est survenue', type: 'error' });
                                                }
                                            })
                                            .catch(_ => {
                                                Notification.createClientNotification({ message: 'Une erreur est survenue', type: 'error' });
                                            });
                                    });
                                }

                            }
                        }
                    });
                });
            }
        }
    }
}

function addEventListenerDom() {
    const formElements = document.querySelectorAll('.playlist-link');
    for (const element of formElements) {
        if (element.classList.contains('disabled')) continue
        if (element.classList.contains('playlist-user-playable')) {
            element.addEventListener('click', eventPlayInMasterSoundboard);
        } else {
            element.addEventListener('click', eventTogglePlaylist);
        }
    }
}

function setUpMixerPlaylist() {
    const mixerPlaylist = new MixerPlaylist();
    mixerPlaylist.addEventListener();
}



function eventTogglePlaylist(event: Event) {
    if (event.target instanceof HTMLElement) {
        const buttonPlaylist = new ButtonPlaylist(event.target)
        if (buttonPlaylist.isActive()) {
            buttonPlaylist.disactive();
            SoundBoardManager.removePlaylist(buttonPlaylist);
        } else {
            buttonPlaylist.active();
            SoundBoardManager.addPlaylist(buttonPlaylist);
        }
    }
}

function eventPlayInMasterSoundboard(event: Event) {
    if (event.target instanceof HTMLElement) {
        const buttonPlaylist = new ButtonPlaylist(event.target)
        if (!buttonPlaylist.isActive()) {
            new SharedSoundboardSendCmdMaster().sendPlayPlaylistOnMaster(buttonPlaylist.getUuid());
            buttonPlaylist.active();
            setTimeout(() => {
                buttonPlaylist.disactive();
            }, Time.get_seconds(1));

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
            SharedSoundBoardWebSocket.getMasterInstance();
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

class ShortcutKeyboardSoundboard {
    shortcutElementsSection: HTMLElement | null;
    ShorcutKeyBoardDetector: ShorcutKeyBoardDetector;
    recoardedShortcuts: Map<string, string> = new Map();
    constructor() {
        this.shortcutElementsSection = document.getElementById('list-shortcut-keyboard');
        this.ShorcutKeyBoardDetector = new ShorcutKeyBoardDetector();
    }

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
                }
            }
        );


    }

    public registerShortcut(shortcut: string, uuidPlaylist: string) {
        this.recoardedShortcuts.set(shortcut, uuidPlaylist);
    }
}


