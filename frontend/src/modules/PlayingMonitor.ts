import { ButtonPlaylistFinder } from '@/modules/ButtonPlaylist';

class PlayingMonitor {
    private readonly LIST_ID = 'playing-monitor-list';
    private readonly EMPTY_ID = 'playing-monitor-empty';
    private readonly TEMPLATE_ID = 'playing-monitor-btn-template';
    private readonly ACTIVE_CLASS = 'active-playlist';
    private readonly CONTENT_CLASS = 'playing-monitor-btn-content';

    private boardObserver: MutationObserver | null = null;
    private readonly buttonObservers: Map<HTMLElement, MutationObserver> = new Map();
    private initialized: boolean = false;

    public init(): void {
        if (this.initialized) return;

        const board = document.querySelector('.responsive-sections-container');
        if (!board) return;

        this.initialized = true;

        this._observeExistingButtons(board);
        // watch for buttons added dynamically (edit mode)
        this.boardObserver = new MutationObserver((mutations) => {
            for (const mutation of mutations) {
                for (const node of mutation.addedNodes) {
                    if (node instanceof HTMLElement) {
                        node.querySelectorAll<HTMLElement>('.playlist-link')
                            .forEach(
                                (el) => this._observeButton(el)
                            );
                    }
                }
            }
        });
        this.boardObserver.observe(board, { childList: true, subtree: true });
    }

    public destroy(): void {
        this.boardObserver?.disconnect();
        this.boardObserver = null;

        for (const observer of this.buttonObservers.values()) {
            observer.disconnect();
        }
        this.buttonObservers.clear();
        this.initialized = false;
    }

    private _observeExistingButtons(board: Element): void {
        board.querySelectorAll<HTMLElement>('.playlist-link').forEach((el) => this._observeButton(el));
    }

    private _observeButton(el: HTMLElement): void {
        if (this.buttonObservers.has(el)) return;

        const observer = new MutationObserver(() => {
            const playlistId = el.dataset.playlistId ?? el.id.replace('playlist-', '');
            if (el.classList.contains(this.ACTIVE_CLASS)) {
                this._addStopButton(playlistId, el);
            } else {
                this._removeStopButton(playlistId);
            }
        });
        observer.observe(el, { attributes: true, attributeFilter: ['class'] });
        this.buttonObservers.set(el, observer);

        const playlistId = el.dataset.playlistId ?? el.id.replace('playlist-', '');
        if (el.classList.contains(this.ACTIVE_CLASS)) {
            this._addStopButton(playlistId, el);
        }
    }

    private _addStopButton(playlistId: string, el: HTMLElement): void {
        if (document.querySelector(`[data-playlist-id="${CSS.escape(playlistId)}"].playing-monitor-stop-btn`)) return;

        const template = document.getElementById(this.TEMPLATE_ID) as HTMLTemplateElement | null;
        if (!template) return;

        const btn = (template.content.cloneNode(true) as DocumentFragment).querySelector<HTMLElement>('button')!;
        btn.dataset.playlistId = playlistId;

        // mirror the source button's visual identity
        btn.setAttribute('style', el.getAttribute('style') ?? '');

        const dimClass = this._getdimclass(el);
        if (dimClass) btn.classList.add(dimClass);

        btn.querySelector(`.${this.CONTENT_CLASS}`)!.innerHTML = el.innerHTML;
        btn.addEventListener('click', () => this._stopPlaylist(playlistId));

        document.getElementById(this.LIST_ID)?.appendChild(btn);
        this._setEmptyVisible(false);
    }

    private _removeStopButton(playlistId: string): void {
        const btn = document.querySelector(`[data-playlist-id="${CSS.escape(playlistId)}"].playing-monitor-stop-btn`);
        btn?.remove();
        const remaining = document.querySelectorAll('.playing-monitor-stop-btn').length;
        this._setEmptyVisible(remaining === 0);
    }

    private _stopPlaylist(playlistId: string): void {
        ButtonPlaylistFinder.search(playlistId)?.simulateClick();
    }

    private _setEmptyVisible(visible: boolean): void {
        const empty = document.getElementById(this.EMPTY_ID);
        if (empty) empty.classList.toggle('d-none', !visible);
    }

    private _getdimclass(el: HTMLElement): string {
        const dimClassOrigin = Array.from(el.classList).find((c) => c.startsWith('playlist-dim-'));
        let dimClass = 100;
        if (dimClassOrigin) {
            const regex = /playlist-dim-(\d+)/;
            const test = regex.exec(dimClassOrigin);
            if (test?.[1]) {
                dimClass = Number.parseInt(test[1]);
                let reduction = 25;
                if (dimClass >= 100) reduction = 50;
                dimClass = Math.max((dimClass - reduction), 50);
            }
        }
        return `playlist-dim-${dimClass}`;

    }
}

export default PlayingMonitor;
