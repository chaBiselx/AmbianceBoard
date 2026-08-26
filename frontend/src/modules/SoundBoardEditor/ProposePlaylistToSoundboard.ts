import Notification from '@/modules/General/Notifications';
import Csrf from '@/modules/General/Csrf';
import ModalCustom from '@/modules/General/Modal';
import { PaginationManager } from '@/modules/PaginationManager';
import FilterFormAjaxManager from '@/modules/Filter/FilterFormAjaxManager';
import PaginationAjaxManager from '@/modules/Filter/PaginationAjaxManager';

const CONTAINER_ID = 'propose-playlist-list-container';

class ProposePlaylistToSoundboard {
    private page = 1;
    private filters: Record<string, string> = {};

    public addEvent(): void {
        this.bindProposeButton();
        this.bindStatusButtons();
    }

    private bindProposeButton(): void {
        const button = document.getElementById('btn-propose-playlist-to-soundboard') as HTMLButtonElement | null;
        if (!button?.dataset.urlList) return;

        button.addEventListener('click', () => this.openModal(button.dataset.urlList!));
    }

    private openModal(listUrl: string): void {
        this.page = 1;
        this.filters = {};

        ModalCustom.show({
            title: 'Proposer une playlist',
            body: `<div id="${CONTAINER_ID}" data-url-list="${listUrl}"></div>`,
            footer: '',
            width: 'lg',
            callback: () => this.loadList(),
        });
    }

    private loadList(): void {
        const container = document.getElementById(CONTAINER_ID);
        if (!container) return;

        const url = container.dataset.urlList;
        if (!url) return;

        const fetchUrl = new URL(url, globalThis.location.origin);
        fetchUrl.searchParams.set(PaginationManager.getParameterName(), this.page.toString());
        for (const [key, value] of Object.entries(this.filters)) {
            if (value) fetchUrl.searchParams.set(key, value);
        }

        fetch(fetchUrl.toString(), {
            method: 'GET',
            headers: { 'X-CSRFToken': Csrf.getToken()! },
        })
            .then((response) => response.text())
            .then((html) => {
                container.innerHTML = html;
                this.bindProposeItemButtons();
                new FilterFormAjaxManager(container, (filters) => {
                    this.filters = filters;
                    this.page = 1;
                    this.loadList();
                }).bind();
                new PaginationAjaxManager(container, (page) => {
                    this.page = page;
                    this.loadList();
                }).bind();
            })
            .catch(() => {
                Notification.createClientNotification({ message: 'Impossible de charger vos playlists', type: 'error' });
            });
    }

    private bindProposeItemButtons(): void {
        const buttons = document.querySelectorAll('.btn-propose-playlist');
        for (const button of buttons) {
            if (!(button instanceof HTMLButtonElement)) continue;
            button.addEventListener('click', () => this.propose(button));
        }
    }

    private propose(button: HTMLButtonElement): void {
        const proposeUrl = button.dataset.urlPropose;
        if (!proposeUrl) return;

        button.setAttribute('disabled', 'true');
        fetch(proposeUrl, {
            method: 'POST',
            headers: { 'X-CSRFToken': Csrf.getToken()! },
        })
            .then(async (response) => {
                const data = await response.json();
                return { data, ok: response.ok };
            })
            .then(({ data, ok }) => {
                if (ok && data.success) {
                    Notification.createClientNotification({ message: data.message || 'Proposition envoyée', type: 'success' });
                    this.loadList();
                } else {
                    Notification.createClientNotification({ message: data.error || 'Une erreur est survenue', type: 'error' });
                    button.removeAttribute('disabled');
                }
            })
            .catch(() => {
                Notification.createClientNotification({ message: 'Une erreur est survenue', type: 'error' });
                button.removeAttribute('disabled');
            });
    }

    private bindStatusButtons(): void {
        const buttons = document.querySelectorAll('.proposal-withdraw-btn, .proposal-dismiss-btn');
        for (const button of buttons) {
            if (!(button instanceof HTMLButtonElement)) continue;
            button.addEventListener('click', () => this.callStatusAction(button));
        }
    }

    private callStatusAction(button: HTMLButtonElement): void {
        const url = button.dataset.url;
        if (!url) return;

        button.setAttribute('disabled', 'true');
        fetch(url, {
            method: 'POST',
            headers: { 'X-CSRFToken': Csrf.getToken()! },
        })
            .then(async (response) => {
                const data = await response.json();
                return { data, ok: response.ok };
            })
            .then(({ data, ok }) => {
                if (ok && data.success) {
                    Notification.createClientNotification({ message: data.message || 'Action effectuée', type: 'success' });
                    globalThis.location.reload();
                } else {
                    Notification.createClientNotification({ message: data.error || 'Une erreur est survenue', type: 'error' });
                    button.removeAttribute('disabled');
                }
            })
            .catch(() => {
                Notification.createClientNotification({ message: 'Une erreur est survenue', type: 'error' });
                button.removeAttribute('disabled');
            });
    }
}

export default ProposePlaylistToSoundboard;
