import { PlayerCustom, PlayerCustomFactory } from '@/modules/Audio/PlayerCustom';
import Csrf from '@/modules/General/Csrf';
import ModalCustom from '@/modules/General/Modal';
import Notification from '@/modules/General/Notifications';
import FilterFormAjaxManager, { type FiltersRecord } from '@/modules/Filter/FilterFormAjaxManager';
import PaginationAjaxManager from '@/modules/Filter/PaginationAjaxManager';
import { PaginationManager } from '@/modules/PaginationManager';

type PlaylistActionResponse = {
    success?: boolean;
    error?: string;
};

export class CommunityPlaylistAdder {
    private readonly button: HTMLButtonElement | null;
    private filters: FiltersRecord = {};
    private previewPlayers: PlayerCustom[] = [];
    private activePreview: PlayerCustom | null = null;
    private requestVersion = 0;
    private isModalOpen = false;

    public constructor() {
        const button = document.getElementById('add-community-playlist-button');
        this.button = button instanceof HTMLButtonElement ? button : null;
    }

    public addEvent(): void {
        if (!this.button) return;

        this.button.addEventListener('click', () => this.openModal());
        ModalCustom.getMainHTMLElement().addEventListener('hide.bs.modal', () => {
            this.isModalOpen = false;
            this.requestVersion++;
            this.disposePreview();
        });
        ModalCustom.getMainHTMLElement().addEventListener('hide.bs.collapse', (event) => {
            if (!(event.target instanceof HTMLElement) || !event.target.matches('.community-track-list')) return;
            for (const player of this.previewPlayers) {
                if (event.target.contains(player.divPlayer)) player.stop(true);
            }
        });
        ModalCustom.getMainHTMLElement().addEventListener('click', (event) => {
            if (!(event.target instanceof Element)) return;
            const duplicateButton = event.target.closest<HTMLButtonElement>('.btn-edit-mode-duplicate');
            if (duplicateButton) {
                event.preventDefault();
                event.stopPropagation();
                void this.duplicatePlaylist(duplicateButton);
            }
        });
    }

    private openModal(): void {
        const listUrl = this.button?.dataset.urlList;
        if (!this.button || !listUrl) return;

        this.filters = {};
        this.isModalOpen = true;
        const loading = document.createElement('div');
        loading.className = 'd-flex justify-content-center mt-3';
        loading.innerHTML = '<output class="spinner-border spinner-border-sm"><span class="visually-hidden"></span></output>';
        const loadingLabel = loading.querySelector('.visually-hidden');
        if (loadingLabel) loadingLabel.textContent = this.button.dataset.loadingMessage || '';

        ModalCustom.show({
            title: this.button.dataset.modalTitle || '',
            body: loading.outerHTML,
            footer: '',
            width: 'lg',
        });
        void this.loadPlaylistList(listUrl, 1);
    }

    private async loadPlaylistList(listUrl: string, page: number): Promise<void> {
        const token = Csrf.getToken();
        if (!token) {
            this.notify(this.button?.dataset.csrfError || 'CSRF token unavailable');
            return;
        }

        const requestVersion = ++this.requestVersion;
        this.disposePreview();
        const url = new URL(listUrl, globalThis.location.origin);
        url.searchParams.set(PaginationManager.getParameterName(), page.toString());
        for (const [key, value] of Object.entries(this.filters)) {
            if (value) url.searchParams.set(key, value);
        }

        try {
            const response = await fetch(url.toString(), {
                method: 'GET',
                headers: { 'X-CSRFToken': token },
            });
            if (!response.ok || response.redirected) throw new Error('Community playlist list unavailable');
            const html = await response.text();
            if (!this.isModalOpen || requestVersion !== this.requestVersion) return;

            const container = document.getElementById('mainModalBody');
            if (!container) throw new Error('Community playlist modal body unavailable');
            container.innerHTML = html;
            this.initializePreview(container);
            new FilterFormAjaxManager(container, (filters) => {
                this.filters = filters;
                void this.loadPlaylistList(listUrl, 1);
            }).bind();
            new PaginationAjaxManager(container, (nextPage) => {
                void this.loadPlaylistList(listUrl, nextPage);
            }).bind();
        } catch {
            if (this.isModalOpen && requestVersion === this.requestVersion) {
                this.notify(this.button?.dataset.loadError || 'Unable to load community playlists');
            }
        }
    }

    private async duplicatePlaylist(button: HTMLButtonElement): Promise<void> {
        const url = button.dataset.urlDuplication;
        const token = Csrf.getToken();
        if (!url) return;
        if (!token) {
            this.notify(this.button?.dataset.csrfError || 'CSRF token unavailable');
            return;
        }

        button.disabled = true;
        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': token,
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({}),
            });
            const data = await response.json() as PlaylistActionResponse;
            if (!response.ok || !data.success) {
                this.notify(data.error || this.button?.dataset.addError || 'Unable to add playlist');
                button.disabled = false;
                return;
            }

            this.isModalOpen = false;
            this.disposePreview();
            ModalCustom.getInstance()?.hide();
            globalThis.location.reload();
        } catch {
            this.notify(this.button?.dataset.addError || 'Unable to add playlist');
            button.disabled = false;
        }
    }

    private initializePreview(container: HTMLElement): void {
        this.previewPlayers = PlayerCustomFactory.create(container, (player) => {
            if (this.activePreview !== player) this.activePreview?.stop(true);
            this.activePreview = player;
        });
    }

    private disposePreview(): void {
        for (const player of this.previewPlayers) player.destroy();
        this.previewPlayers = [];
        this.activePreview = null;
    }

    private notify(message: string): void {
        Notification.createClientNotification({ message, type: 'danger' });
    }
}
