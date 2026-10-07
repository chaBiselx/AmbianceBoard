import Notification from '@/modules/General/Notifications';
import Csrf from "@/modules/General/Csrf";
import ModalCustom from '@/modules/General/Modal';
import PopupAddMusicToSoundboard from '@/modules/SoundBoardEditor/PopupAddMusicToSoundboard';
import SoundBoardEventListener from '@/modules/SoundBoardEventListener';
import { MixerManager } from '@/modules/MixerManager';
import { PaginationManager } from '@/modules/PaginationManager';
import FilterFormAjaxManager from '@/modules/Filter/FilterFormAjaxManager';
import PaginationAjaxManager from '@/modules/Filter/PaginationAjaxManager';
import { PlayerCustom, PlayerCustomFactory } from '@/modules/Audio/PlayerCustom';


class SoundboardEditMode {
    private isEditModeActive = false;
    private panelUrl: string | null = null;
    private boardContainer: HTMLElement | null = null;
    private playlistListFilters: Record<string, string> = {};
    private myPlaylistListFilters: Record<string, string> = {};
    private buttonAction: HTMLButtonElement | null = null;
    private readonly id_section_add_button: string = 'soundboard-add-section-button';
    private activeAddZone: HTMLElement | null = null;
    private previewPlayers: PlayerCustom[] = [];
    private activePreview: PlayerCustom | null = null;
    private previewListeners: AbortController | null = null;
    private previewRequestVersion = 0;

    public addEvent(): void {
        this.buttonAction = document.getElementById('btn-soundboard-edit-mode') as HTMLButtonElement | null;
        if (!this.buttonAction) return;

        if (!(this.buttonAction instanceof HTMLButtonElement)) return;
        this.panelUrl = this.buttonAction.dataset.urlPanel || null;
        this.boardContainer = document.querySelector('[data-soundboard-editable="true"]');

        if (!this.boardContainer || !this.panelUrl) return;

        this.buttonAction.setAttribute('aria-pressed', 'false');

        this.buttonAction.addEventListener('click', () => {
            this.toggleEditMode(this.buttonAction!);
        });

        this.bindAddZones();
        this.bindAddMusicButtons();
        this.bindAddSectionButton();
        this._startIfEmpty();
    }

    private toggleSoundboardMenuEdition(): void {
        const menuEdition = document.querySelector('.soundboard-menu-edition');
        if (!menuEdition) return;
        menuEdition.classList.toggle('d-none', !this.isEditModeActive);
    }

    private toggleEditMode(button: HTMLButtonElement): void {
        if (!this.boardContainer) return;

        this.isEditModeActive = !this.isEditModeActive;
        this.boardContainer.classList.toggle('soundboard-edit-mode-active', this.isEditModeActive);
        button.setAttribute('aria-pressed', this.isEditModeActive ? 'true' : 'false');
        button.classList.toggle('btn-outline-success', !this.isEditModeActive);
        button.classList.toggle('btn-success', this.isEditModeActive);
        this.toggleSoundboardMenuEdition();
        const addSectionButton = document.getElementById(this.id_section_add_button) as HTMLButtonElement | null;
        if (addSectionButton) {
            addSectionButton.classList.toggle('d-none', !this.isEditModeActive);
        }

    }

    private _startIfEmpty(): void {
        const listPlaylistElement = document.querySelectorAll('.responsive-sections-container .playlist-link');
        const lengthPlaylistElement = listPlaylistElement?.length ?? 0;
        if(lengthPlaylistElement === 0) {
            this.buttonAction?.click();
            this.toggleSoundboardMenuEdition();
        }
    }

    private bindAddZones(): void {
        if (!this.boardContainer) return;
        this.bindAddZonesIn(this.boardContainer);
    }

    /** Rebind les zones d'ajout ("Ajouter") présentes dans un noeud ajouté dynamiquement (ex: nouvelle section). */
    public bindAddZonesIn(root: ParentNode): void {
        const zones = root.querySelectorAll('[data-soundboard-edit-open-panel="true"]');
        for (const zone of zones) {
            if (!(zone instanceof HTMLButtonElement)) continue;
            zone.addEventListener('click', () => {
                if (!this.isEditModeActive) return;
                this.activeAddZone = zone;
                this.openPanel();
            });
        }
    }

    /** Délégation sur le conteneur : couvre aussi les boutons insérés dynamiquement. */
    private bindAddMusicButtons(): void {
        this.boardContainer?.addEventListener('click', (event) => {
            if (!this.isEditModeActive) return;
            const target = event.target as HTMLElement | null;
            const button = target?.closest<HTMLButtonElement>('[data-soundboard-edit-add-music-url]');
            const url = button?.dataset.soundboardEditAddMusicUrl;
            if (!button || !url) return;
            event.stopPropagation();
            if (button.dataset.clicked === 'active') return;
            button.dataset.clicked = 'active';
            button.setAttribute("disabled", "true");
            setTimeout(() => {
                delete button.dataset.clicked;
                button.removeAttribute("disabled");
            }, 300);
            new PopupAddMusicToSoundboard(url).showIfValue();
        });
    }

    private bindAddSectionButton(): void {
        const addSectionButton = document.getElementById(this.id_section_add_button) as HTMLButtonElement | null;
        if (!addSectionButton) return;

        addSectionButton.addEventListener('click', () => {
            if (!this.isEditModeActive) return;
        });
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
            .then(response => {
                if (response.redirected || response.ok === false) throw new Error('Panel unavailable');
                return response.text();
            })
            .then((body) => {
                ModalCustom.show({
                    title: "Ajouter un bouton",
                    body: body,
                    footer: "",
                    width: "lg",
                    callback: () => {
                        this.bindCommunityPreviewLifecycle();
                        this.bindCreateForm();
                        this.loadPlaylistList();
                        this.loadMyPlaylistList();
                    }
                });
            })
            .catch(() => {
                Notification.createClientNotification({ message: 'Impossible de charger le mode édition', type: 'danger' });
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
        const section = this.activeAddZone?.dataset.section;
        if (section) formData.set('section', section);

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
                    type: 'danger'
                });
                submitBtn.disabled = false;
            })
            .catch(() => {
                Notification.createClientNotification({
                    message: 'Erreur de communication avec le serveur',
                    type: 'danger'
                });
                submitBtn.disabled = false;
            });
    }

    private insertPlaylistToBoard(html: string): void {
        const flexContainer = this.activeAddZone?.closest('.flex-container')
            ?? document.querySelector('.responsive-sections-container .flex-container');
        if (!flexContainer) return;

        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = html;
        const playlistItem = tempDiv.firstElementChild;
        if (playlistItem) {
            // Insérer avant la zone d'ajout cliquée (ou la première à défaut) pour rester dans la bonne section
            const addZone = this.activeAddZone ?? flexContainer.querySelector('.soundboard-edit-add-zone');
            if (addZone?.parentElement === flexContainer) {
                addZone.before(playlistItem);
            } else {
                flexContainer.appendChild(playlistItem);
            }
        }

        // Rebind event listeners for the new playlist
        new SoundBoardEventListener().addEventListenerDom();
        new MixerManager().initializeEventListeners();
        MixerManager.updatePlaylistVolumeWidths();
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

    private bindCommunityPreviewLifecycle(): void {
        this.disposeCommunityPreview();
        this.previewListeners?.abort();
        this.previewListeners = new AbortController();
        const options = { signal: this.previewListeners.signal };
        const modal = document.getElementById('mainModal');
        modal?.addEventListener('hide.bs.modal', () => {
            this.disposeCommunityPreview();
            this.previewListeners?.abort();
            this.previewListeners = null;
        }, options);
        modal?.addEventListener('hide.bs.tab', () => this.stopCommunityPreview(), options);
        modal?.addEventListener('hide.bs.collapse', (event) => {
            if (!(event.target instanceof HTMLElement) || !event.target.matches('.community-track-list')) return;
            const list = event.target;
            for (const player of this.previewPlayers) {
                if (list.contains(player.divPlayer)) player.stop(true);
            }
        }, options);
    }

    private initializeCommunityPreview(): void {
        const container = document.getElementById('soundboard-edit-playlist-list-container');
        if (!container) return;
        this.previewPlayers = PlayerCustomFactory.create(container, (player) => {
            if (this.activePreview !== player) this.activePreview?.stop(true);
            this.activePreview = player;
        });
    }

    private stopCommunityPreview(): void {
        for (const player of this.previewPlayers) player.stop(true);
        this.activePreview = null;
    }

    private disposeCommunityPreview(): void {
        this.previewRequestVersion++;
        for (const player of this.previewPlayers) player.destroy();
        this.previewPlayers = [];
        this.activePreview = null;
    }

    private loadPlaylistList(page = 1): void {
        this.loadListInContainer(
            'soundboard-edit-playlist-list-container',
            page,
            this.playlistListFilters,
            () => {
                this.bindDuplicateButtons();
                this.initializeCommunityPreview();
            },
            (p) => this.loadPlaylistList(p),
            (filters) => {
                this.playlistListFilters = filters;
                this.loadPlaylistList(1);
            },
            'Impossible de charger la liste'
        );
    }

    private loadMyPlaylistList(page = 1): void {
        this.loadListInContainer(
            'soundboard-edit-my-playlist-list-container',
            page,
            this.myPlaylistListFilters,
            () => this.bindAddMyPlaylistButtons(),
            (p) => this.loadMyPlaylistList(p),
            (filters) => {
                this.myPlaylistListFilters = filters;
                this.loadMyPlaylistList(1);
            },
            'Impossible de charger mes playlists'
        );
    }

    private loadListInContainer(
        containerId: string,
        page: number,
        filters: Record<string, string>,
        onLoaded: () => void,
        onPageChange: (page: number) => void,
        onFiltersChange: (filters: Record<string, string>) => void,
        errorMessage: string
    ): void {
        const container = document.getElementById(containerId);
        if (!container) return;

        const url = container.dataset.urlList;
        if (!url) return;

        const isCommunityList = containerId === 'soundboard-edit-playlist-list-container';
        if (isCommunityList) this.stopCommunityPreview();
        const requestVersion = isCommunityList ? ++this.previewRequestVersion : 0;

        const fetchUrl = new URL(url, globalThis.location.origin);
        fetchUrl.searchParams.set(PaginationManager.getParameterName(), page.toString());
        for (const [key, value] of Object.entries(filters)) {
            if (!value) continue;
            fetchUrl.searchParams.set(key, value);
        }

        fetch(fetchUrl.toString(), {
            method: 'GET',
            headers: { 'X-CSRFToken': Csrf.getToken()! },
        })
            .then(response => {
                if (response.redirected || response.ok === false) throw new Error('List unavailable');
                return response.text();
            })
            .then(html => {
                if (!container.isConnected || (isCommunityList && requestVersion !== this.previewRequestVersion)) return;
                if (isCommunityList) this.disposeCommunityPreview();
                container.innerHTML = html;
                onLoaded();
                this.bindPaginationInContainer(container, onPageChange);
                this.bindFiltersInContainer(container, onFiltersChange);
            })
            .catch(() => {
                Notification.createClientNotification({ message: errorMessage, type: 'danger' });
            });
    }

    private bindFiltersInContainer(
        container: HTMLElement,
        onFiltersChange: (filters: Record<string, string>) => void
    ): void {
        new FilterFormAjaxManager(container, onFiltersChange).bind();
    }

    private bindPaginationInContainer(container: HTMLElement, onPageChange: (page: number) => void): void {
        new PaginationAjaxManager(container, onPageChange).bind();
    }

    private bindAddMyPlaylistButtons(): void {
        const buttons = document.querySelectorAll('.btn-edit-mode-add-my-playlist');
        for (const button of buttons) {
            if (!(button instanceof HTMLButtonElement)) continue;
            button.addEventListener('click', () => {
                this.addMyPlaylist(button);
            });
        }
    }

    private addMyPlaylist(button: HTMLButtonElement): void {
        const url = button.dataset.urlAdd;
        if (!url) return;
        this.postPlaylistAction(url, button);
    }

    private duplicatePlaylist(button: HTMLButtonElement): void {
        const url = button.dataset.urlDuplication;
        if (!url) return;
        this.stopCommunityPreview();
        this.postPlaylistAction(url, button);
    }

    private postPlaylistAction(url: string, button: HTMLButtonElement): void {
        button.disabled = true;
        const section = this.activeAddZone?.dataset.section;
        let body: { section: number | null } = { section: null };
        if (section) body.section = Number.parseInt(section);
        fetch(url, {
            method: 'POST',
            headers: {
                'X-CSRFToken': Csrf.getToken()!,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(body),
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
                    type: 'danger'
                });
                button.disabled = false;
            })
            .catch(() => {
                Notification.createClientNotification({
                    message: 'Erreur de communication avec le serveur',
                    type: 'danger'
                });
                button.disabled = false;
            });
    }
}

export default SoundboardEditMode;