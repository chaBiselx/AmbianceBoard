import { ButtonPlaylist } from '@/modules/ButtonPlaylist';
import { MusicElement } from '@/modules/MusicElement';
import { SoundBoardManager } from '@/modules/SoundBoardManager';
import UpdateVolumeElement from '@/modules/UpdateVolumeElement';

type PreviewDependencies = {
    fetch: typeof fetch;
    showModal: (options: { title: string; body: string; footer: string; width: string; callback: () => void }) => void;
    notify: (message: string) => void;
};

export class PlaylistPlaybackPreview {
    private readonly button: ButtonPlaylist;
    private readonly listeners = new AbortController();
    private readonly rows = new Map<MusicElement, { row: HTMLElement; name: HTMLElement; time: HTMLElement }>();
    private readonly interval: ReturnType<typeof setInterval>;
    private destroyed = false;

    constructor(private readonly root: HTMLElement) {
        this.button = new ButtonPlaylist(root.querySelector<HTMLElement>('[data-playlist-preview]')!);
        this.button.buttonElement.addEventListener('click', () => this.toggle(), { signal: this.listeners.signal });
        root.querySelector<HTMLInputElement>('#playlist-preview-volume')!.addEventListener('input', () => this.updateVolume(), { signal: this.listeners.signal });
        this.interval = setInterval(() => this.render(), 250);
        this.render();
    }

    private toggle(): void {
        if (this.destroyed) return;
        delete this.button.dataset.previewError;
        if (this.button.isActive()) {
            this.button.disactive();
            SoundBoardManager.removePlaylist(this.button);
        } else {
            for (const audio of document.querySelectorAll<HTMLAudioElement>('audio.music-player')) {
                audio.pause();
                const player = audio.closest('.player-custom');
                player?.querySelector('.pause-icon')?.classList.add('d-none');
                player?.querySelector('.play-icon')?.classList.remove('d-none');
            }
            this.button.active();
            SoundBoardManager.addPlaylist(this.button);
        }
        this.render();
    }

    private updateVolume(): void {
        if (this.destroyed) return;
        const volume = this.root.querySelector<HTMLInputElement>('#playlist-preview-volume')!.valueAsNumber;
        this.button.setVolume(volume);
        this.root.querySelector<HTMLOutputElement>('[data-preview-volume-value]')!.value = `${volume} %`;
        for (const element of MusicElement.getPreviewElements()) {
            element.setDefaultVolume(volume / 100);
            new UpdateVolumeElement(element).update();
        }
    }

    private render(): void {
        const elements = MusicElement.getPreviewElements();
        const active = this.button.isActive();
        this.button.buttonElement.setAttribute('aria-pressed', String(active));
        const status = this.root.querySelector<HTMLElement>('[data-preview-status]')!;
        let statusText: string;
        if (this.button.dataset.previewError === 'true') {
            statusText = this.root.dataset.error!;
        } else if (elements.length) {
            statusText = '';
        } else if (active) {
            statusText = this.root.dataset.waiting!;
        } else {
            statusText = this.root.dataset.idle!;
        }
        status.textContent = statusText;

        for (const [element, { row }] of this.rows) {
            if (!elements.includes(element)) {
                row.remove();
                this.rows.delete(element);
            }
        }
        for (const element of elements) {
            let controls = this.rows.get(element);
            if (!controls) {
                const row = document.createElement('div');
                row.className = 'd-flex flex-wrap justify-content-between gap-2 py-2 border-bottom';
                const name = document.createElement('span');
                name.className = 'text-break';
                const time = document.createElement('span');
                time.className = 'font-monospace text-nowrap';
                row.append(name, time);
                this.root.querySelector('[data-preview-tracks]')!.append(row);
                controls = { row, name, time };
                this.rows.set(element, controls);
            }
            const state = element.getPlaybackState();
            controls.name.textContent = state.name || this.root.dataset.waiting!;
            controls.time.textContent = `${formatTime(state.currentTime)} / ${formatTime(state.duration)}`;
        }
    }

    destroy(): void {
        if (this.destroyed) return;
        this.destroyed = true;
        this.button.disactive();
        this.listeners.abort();
        clearInterval(this.interval);
        MusicElement.disposePreview();
        this.rows.clear();
    }
}

function formatTime(seconds: number | null): string {
    if (seconds === null || !Number.isFinite(seconds)) return '--:--';
    const total = Math.max(0, Math.floor(seconds));
    return `${Math.floor(total / 60)}:${String(total % 60).padStart(2, '0')}`;
}

export function initializePlaylistPlaybackPreview(dependencies: PreviewDependencies, doc: Document = document): void {
    const trigger = doc.getElementById('btn-test-playlist') as HTMLButtonElement | null;
    const modal = doc.getElementById('mainModal');
    if (!trigger || trigger.disabled || !modal) return;
    let pending: AbortController | null = null;
    let preview: PlaylistPlaybackPreview | null = null;
    let observer: MutationObserver | null = null;

    const cleanup = () => {
        pending?.abort();
        observer?.disconnect();
        preview?.destroy();
        preview = null;
    };
    modal.addEventListener('hide.bs.modal', cleanup);
    modal.addEventListener('hidden.bs.modal', () => trigger.focus());
    doc.defaultView?.addEventListener('pagehide', cleanup);

    trigger.addEventListener('click', async () => {
        cleanup();
        const request = new AbortController();
        pending = request;
        trigger.disabled = true;
        trigger.setAttribute('aria-busy', 'true');
        try {
            const response = await dependencies.fetch(trigger.dataset.url!, { signal: request.signal });
            if (!response.ok || response.redirected) throw new Error('Preview unavailable');
            const body = await response.text();
            if (request.signal.aborted) return;
            dependencies.showModal({
                title: trigger.dataset.modalTitle!, body, footer: '', width: 'lg',
                callback: () => {
                    const root = modal.querySelector<HTMLElement>('[data-playlist-playback-preview]');
                    if (!root) return;
                    preview = new PlaylistPlaybackPreview(root);
                    observer = new MutationObserver(() => { if (!root.isConnected) cleanup(); });
                    observer.observe(modal, { childList: true, subtree: true });
                },
            });
        } catch {
            if (!request.signal.aborted) dependencies.notify(trigger.dataset.error!);
        } finally {
            if (pending === request) {
                trigger.disabled = false;
                trigger.removeAttribute('aria-busy');
            }
        }
    });
}