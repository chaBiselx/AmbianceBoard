
import Config from '@/modules/General/Config';
import Csrf from "@/modules/General/Csrf";
import Cookie from '@/modules/General/Cookie';

import { ButtonPlaylistFinder } from '@/modules/ButtonPlaylist';
import { MixerManager } from '@/modules/MixerManager';
import WakeLock from '@/modules/General/WakeLock';
import ModalCustom from '@/modules/General/Modal';
import SharedSoundBoardWebSocket from '@/modules/SharedSoundBoardWebSocket';
import SharedSoundBoardUtil from '@/modules/SharedSoundBoardUtil';
import { MixerPlaylist } from "@/modules/MixerPlaylist";
import ShareLinkManager from '@/modules/Event/ShareLinkManager';
import ConsoleTesteur from '@/modules/General/ConsoleTesteur';
import { SharedSoundboardCustomVolumeFactory } from '@/modules/SharedSoundboardCustomVolume';
import ShorcutKeyBoardDetector from "@/modules/Control/ShorcutKeyBoardDetector";
import ConsoleCustom from "@/modules/General/ConsoleCustom";
import { MusicDropzoneConfig, MusicDropzoneManager } from '@/modules/MusicDropzoneManager';
import Notification from '@/modules/General/Notifications';
import SoundBoardEventListener from '@/modules/SoundBoardEventListener';
import StreamConnectionWarmup from '@/modules/StreamConnectionWarmup';
import { PaginationManager } from '@/modules/PaginationManager';




document.addEventListener("DOMContentLoaded", () => {
    // Why: reduire la latence percue du premier clic playlist.
    // How: prechauffe DNS/TCP/TLS vers l'origine de stream via StreamConnectionWarmup.
    new StreamConnectionWarmup().initialize();
    showPopupSharedPlaylist();
    new SoundBoardEventListener().addEventListenerDom();
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
    new SoundboardEditMode().addEvent();

    // Initialiser automatiquement le WebSocket si on est en mode master
    initializeWebSocketIfMaster();
});

class SoundboardEditMode {
    private isEditModeActive = false;
    private panelUrl: string | null = null;
    private boardContainer: HTMLElement | null = null;

    public addEvent(): void {
        const button = document.getElementById('btn-soundboard-edit-mode');
        if (!button) return;

        if (!(button instanceof HTMLButtonElement)) return;
        this.panelUrl = button.dataset.urlPanel || null;
        this.boardContainer = document.querySelector('[data-soundboard-editable="true"]');

        if (!this.boardContainer || !this.panelUrl) return;

        button.setAttribute('aria-pressed', 'false');

        button.addEventListener('click', () => {
            this.toggleEditMode(button);
        });

        this.bindAddZones();
    }

    private toggleEditMode(button: HTMLButtonElement): void {
        if (!this.boardContainer) return;

        this.isEditModeActive = !this.isEditModeActive;
        this.boardContainer.classList.toggle('soundboard-edit-mode-active', this.isEditModeActive);
        button.setAttribute('aria-pressed', this.isEditModeActive ? 'true' : 'false');
        button.classList.toggle('btn-outline-success', !this.isEditModeActive);
        button.classList.toggle('btn-success', this.isEditModeActive);
    }

    private bindAddZones(): void {
        if (!this.boardContainer) return;

        const zones = this.boardContainer.querySelectorAll('[data-soundboard-edit-open-panel="true"]');
        for (const zone of zones) {
            if (!(zone instanceof HTMLButtonElement)) continue;
            zone.addEventListener('click', () => {
                if (!this.isEditModeActive) return;
                this.openPanel();
            });
        }
    }

    private openPanel(): void {
        const panelUrl = this.panelUrl;
        if (!panelUrl) return;

        fetch(panelUrl, {
            method: 'GET',
            headers: {
                'X-CSRFToken': Csrf.getToken()!
            }
        })
            .then(response => response.text())
            .then((body) => {
                ModalCustom.show({
                    title: "Ajouter une playlist",
                    body: body,
                    footer: "",
                    width: "lg",
                    callback: () => {
                        this.bindCreateForm();
                        this.loadPlaylistList();
                    }
                });
            })
            .catch(() => {
                Notification.createClientNotification({ message: 'Impossible de charger le mode édition', type: 'error' });
            });
    }

    private bindCreateForm(): void {
        const form = document.getElementById('soundboard-edit-mode-create-form');
        const submitBtn = document.getElementById('soundboard-edit-mode-create-submit') as HTMLButtonElement | null;
        if (!(form instanceof HTMLFormElement) || !submitBtn) return;

        form.addEventListener('submit', (event) => {
            event.preventDefault();
            this.createPlaylist(form, submitBtn);
        });
    }

    private createPlaylist(form: HTMLFormElement, submitBtn: HTMLButtonElement): void {
        const createUrl = form.dataset.urlCreate;
        if (!createUrl) return;

        submitBtn.disabled = true;
        const formData = new FormData(form);

        fetch(createUrl, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': Csrf.getToken()!,
            },
        })
            .then(async response => {
                const data = await response.json();
                return { response, data };
            })
            .then(({ response, data }) => {
                if (response.ok && data.success) {
                    Notification.createClientNotification({
                        message: data.message || 'Playlist créée',
                        type: 'success'
                    });

                    const playlistHtml = data.playlist_html as string | undefined;
                    const addMusicUrl = data.add_music_url as string | undefined;

                    const bsModal = ModalCustom.getInstance();
                    if (bsModal) {
                        bsModal.hide();
                    }
                    if (addMusicUrl) {

                        setTimeout(() => {
                            const popup = new PopupAddMusicToSoundboard(addMusicUrl);
                            popup.showIfValue();
                            if (playlistHtml) {
                                this.insertPlaylistToBoard(playlistHtml);
                            }
                        }, 300);
                    }
                    return;
                }

                Notification.createClientNotification({
                    message: data.error || 'Une erreur est survenue',
                    type: 'error'
                });
                submitBtn.disabled = false;
            })
            .catch(() => {
                Notification.createClientNotification({
                    message: 'Erreur de communication avec le serveur',
                    type: 'error'
                });
                submitBtn.disabled = false;
            });
    }

    private insertPlaylistToBoard(html: string): void {
        const flexContainer = document.querySelector('.responsive-sections-container .flex-container');
        if (!flexContainer) return;

        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = html;
        const playlistItem = tempDiv.firstElementChild;
        if (playlistItem) {
            // Insérer avant la première zone d'ajout (soundboard-edit-add-zone) si elle existe
            const firstAddZone = flexContainer.querySelector('.soundboard-edit-add-zone');
            if (firstAddZone) {
                firstAddZone.before(playlistItem);
            } else {
                flexContainer.appendChild(playlistItem);
            }
        }

        // Rebind event listeners for the new playlist
        new SoundBoardEventListener().addEventListenerDom();
        new MixerManager().initializeEventListeners();
        updateWithMixerPlaylist();
    }

    private bindDuplicateButtons(): void {
        const buttons = document.querySelectorAll('.btn-edit-mode-duplicate');
        for (const button of buttons) {
            if (!(button instanceof HTMLButtonElement)) continue;
            button.addEventListener('click', () => {
                this.duplicatePlaylist(button);
            });
        }
    }

    private loadPlaylistList(page = 1): void {
        const container = document.getElementById('soundboard-edit-playlist-list-container');
        if (!container) return;

        const url = container.dataset.urlList;
        if (!url) return;

        const fetchUrl = new URL(url, globalThis.location.origin);
        fetchUrl.searchParams.set(PaginationManager.getParameterName(), page.toString());

        fetch(fetchUrl.toString(), {
            method: 'GET',
            headers: { 'X-CSRFToken': Csrf.getToken()! },
        })
            .then(response => response.text())
            .then(html => {
                container.innerHTML = html;
                this.bindDuplicateButtons();
                this.bindPaginationInContainer(container);
            })
            .catch(() => {
                Notification.createClientNotification({ message: 'Impossible de charger la liste', type: 'error' });
            });
    }

    private bindPaginationInContainer(container: HTMLElement): void {
        const paginationButtons = container.querySelectorAll('#pagination .page-item');
        for (const pageItem of paginationButtons) {
            if (pageItem.classList.contains('disabled')) continue;
            const button = pageItem.querySelector('.page-link') as HTMLButtonElement | null;
            if (!button) continue;
            button.addEventListener('click', (event) => {
                const target = event.target as HTMLElement;
                const page = target.dataset.page;
                if (page) {
                    this.loadPlaylistList(Number.parseInt(page, 10));
                }
            });
        }
    }

    private duplicatePlaylist(button: HTMLButtonElement): void {
        const url = button.dataset.urlDuplication;
        if (!url) return;

        button.disabled = true;
        fetch(url, {
            method: 'POST',
            headers: {
                'X-CSRFToken': Csrf.getToken()!,
            },
        })
            .then(async response => {
                const data = await response.json();
                return { response, data };
            })
            .then(({ response, data }) => {
                if (response.ok && data.success) {
                    Notification.createClientNotification({
                        message: data.message || 'Playlist ajoutée',
                        type: 'success'
                    });

                    const playlistHtml = data.playlist_html as string | undefined;
                    if (playlistHtml) {
                        this.insertPlaylistToBoard(playlistHtml);
                    }

                    const bsModal = ModalCustom.getInstance();
                    if (bsModal) {
                        bsModal.hide();
                    }
                    return;
                }

                Notification.createClientNotification({
                    message: data.error || 'Une erreur est survenue',
                    type: 'error'
                });
                button.disabled = false;
            })
            .catch(() => {
                Notification.createClientNotification({
                    message: 'Erreur de communication avec le serveur',
                    type: 'error'
                });
                button.disabled = false;
            });
    }
}

/**
 * Handles modal interactions for adding music to the soundboard.
 */
class AddMusicModalHandler {
    /**
     * Sets up the music dropzone for file uploads.
     * @returns {void}
     */
    private initializeDropzone(): void {
        const dropZone = document.getElementById('music-dropzone');
        if (!dropZone) return;

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

    /**
     * Configures navigation between different sections of the add music modal.
     * @returns {void}
     */
    private setupSectionNavigation(): void {
        const sectionAction = document.getElementById('selection-type-ajout');
        const sectionAddFile = document.getElementById('form-add-music-from-soundboard');
        const sectionAddLink = document.getElementById('form-add-link-from-soundboard');

        if (!sectionAction || !sectionAddFile || !sectionAddLink) return;

        this.setupAddMusicFileButton(sectionAction, sectionAddFile);
        this.setupAddMusicLinkButton(sectionAction, sectionAddLink);
        this.setupLinkSubmitForm();
    }

    /**
     * Configures the button that allows users to add music from a file.
     * @param {HTMLElement} sectionAction - The action selection section element
     * @param {HTMLElement} sectionAddFile - The file upload section element
     * @returns {void}
     */
    private setupAddMusicFileButton(sectionAction: HTMLElement, sectionAddFile: HTMLElement): void {
        const addMusicFile = document.getElementById('btn-add-music-from-soundboard');
        if (addMusicFile) {
            addMusicFile.addEventListener('click', () => {
                sectionAction.classList.add('d-none');
                sectionAddFile.classList.remove('d-none');
            });
        }
    }

    /**
     * Configures the button that allows users to add music from a link.
     * @param {HTMLElement} sectionAction - The action selection section element
     * @param {HTMLElement} sectionAddLink - The link input section element
     * @returns {void}
     */
    private setupAddMusicLinkButton(sectionAction: HTMLElement, sectionAddLink: HTMLElement): void {
        const addMusicLink = document.getElementById('btn-add-link-from-soundboard');
        if (addMusicLink) {
            addMusicLink.addEventListener('click', () => {
                sectionAction.classList.add('d-none');
                sectionAddLink.classList.remove('d-none');
            });
        }
    }

    /**
     * Configures the form submission behavior for adding music via link.
     * @returns {void}
     */
    private setupLinkSubmitForm(): void {
        const form = document.getElementById('form-add-link-music-ajax');
        const submitBtn = document.getElementById('submit-add-link-ajax') as HTMLButtonElement | null;

        if (!submitBtn || !(form instanceof HTMLFormElement)) return;

        submitBtn.addEventListener('click', (e) => {
            e.preventDefault();
            this.handleLinkSubmit(form);
        });
    }

    /**
     * Processes the link submission request and displays the result to the user.
     * @param {HTMLFormElement} form - The form element containing the music link
     * @returns {void}
     */
    private handleLinkSubmit(form: HTMLFormElement): void {
        const formData = new FormData(form);
        const url = form.action;
        const submitBtn = form.querySelector('button[type="submit"]');

        // Désactiver le bouton pendant l'envoi
        if (submitBtn instanceof HTMLButtonElement) {
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
            })
            .finally(() => {
                if (submitBtn instanceof HTMLButtonElement) {
                    submitBtn.disabled = false;
                    submitBtn.textContent = 'Envoyer';
                }
            });
    }

    /**
     * Initializes all components of the add music modal.
     * @returns {void}
     */
    public initialize(): void {
        this.initializeDropzone();
        this.setupSectionNavigation();
    }
}

/**
 * Manages the display of the popup for adding music to a soundboard.
 */
class PopupAddMusicToSoundboard {

    url: string;

    /**
     * Creates a new popup manager instance.
     * Can be called with or without parameters for backward compatibility.
     */
    constructor(url: string) {
        this.url = url;
    }

    /**
     * Displays the popup if the necessary values are present.
     * @returns {void}
     */
    public showIfValue(): void {
        fetch(this.url, {
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
                    const handler = new AddMusicModalHandler();
                    handler.initialize();
                }
            });
        });
    }

}

/**
 * Initializes the mixer playlist and attaches necessary event listeners.
 * @returns {void}
 */
function setUpMixerPlaylist() {
    const mixerPlaylist = new MixerPlaylist();
    mixerPlaylist.addEventListener();
}

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
 * Updates the volume control width to match the playlist elements.
 * @returns {void}
 */
function updateWithMixerPlaylist() {
    const formElements = document.getElementsByClassName(`playlist-link`) as HTMLCollectionOf<HTMLAudioElement>;
    for (const element of formElements) {
        const elmentDest = document.getElementById(`range_volume_${element.dataset.playlistId!}`)
        if (elmentDest) {
            elmentDest.style.width = `${element.offsetWidth}px`;
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


