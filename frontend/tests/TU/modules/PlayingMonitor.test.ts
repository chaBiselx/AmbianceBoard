import { beforeEach, describe, expect, it, vi } from 'vitest';
import PlayingMonitor from '@/modules/PlayingMonitor';
import { ButtonPlaylistFinder } from '@/modules/ButtonPlaylist';

vi.mock('@/modules/ButtonPlaylist', () => ({
    ButtonPlaylistFinder: {
        search: vi.fn()
    }
}));

const flushMutationObservers = async () => {
    await new Promise((resolve) => setTimeout(resolve, 0));
};

const setupDOM = (playlistClass = 'playlist-dim-150', active = false): HTMLElement => {
    document.body.innerHTML = `
        <div class="responsive-sections-container">
            <div
                id="playlist-abc"
                class="playlist-link ${playlistClass} ${active ? 'active-playlist' : ''}"
                style="background-color: rgb(0, 0, 0); color: rgb(255, 255, 255);"
            >
                <span>Thunder</span>
            </div>
        </div>

        <div id="playing-monitor-list">
            <span id="playing-monitor-empty">empty</span>
        </div>

        <template id="playing-monitor-btn-template">
            <button class="playlist-element playing-monitor-stop-btn m-1 position-relative" data-playlist-id="">
                <span class="playing-monitor-btn-content"></span>
                <span class="playing-monitor-stop-badge"><i class="fa-solid fa-stop"></i></span>
            </button>
        </template>
    `;

    return document.getElementById('playlist-abc') as HTMLElement;
};

describe('PlayingMonitor', () => {
    beforeEach(() => {
        vi.clearAllMocks();
        vi.stubGlobal('alert', vi.fn());
        document.body.innerHTML = '';
    });

    it('should create monitor button from an already active playlist at init with big', async () => {
        setupDOM('playlist-dim-150', true);
        const monitor = new PlayingMonitor();

        monitor.init();
        await flushMutationObservers();

        const stopBtn = document.querySelector('.playing-monitor-stop-btn') as HTMLElement;
        expect(stopBtn).not.toBeNull();
        expect(stopBtn.dataset.playlistId).toBe('abc');
        expect(stopBtn.classList.contains('playlist-dim-100')).toBe(true);
        expect(stopBtn.querySelector('.playing-monitor-btn-content')?.innerHTML).toContain('Thunder');
        expect(stopBtn.getAttribute('style')).toContain('background-color');
    });

    it('should create monitor button from an already active playlist at init with small', async () => {
        setupDOM('playlist-dim-75', true);
        const monitor = new PlayingMonitor();

        monitor.init();
        await flushMutationObservers();

        const stopBtn = document.querySelector('.playing-monitor-stop-btn') as HTMLElement;
        expect(stopBtn).not.toBeNull();
        expect(stopBtn.dataset.playlistId).toBe('abc');
        expect(stopBtn.classList.contains('playlist-dim-50')).toBe(true);
        expect(stopBtn.querySelector('.playing-monitor-btn-content')?.innerHTML).toContain('Thunder');
        expect(stopBtn.getAttribute('style')).toContain('background-color');
    });

    it('should add then remove monitor button when active-playlist class toggles', async () => {
        const sourceBtn = setupDOM('playlist-dim-100', false);
        const monitor = new PlayingMonitor();

        monitor.init();
        sourceBtn.classList.add('active-playlist');
        await flushMutationObservers();

        expect(document.querySelectorAll('.playing-monitor-stop-btn')).toHaveLength(1);
        expect(document.getElementById('playing-monitor-empty')?.classList.contains('d-none')).toBe(true);

        sourceBtn.classList.remove('active-playlist');
        await flushMutationObservers();

        expect(document.querySelectorAll('.playing-monitor-stop-btn')).toHaveLength(0);
        expect(document.getElementById('playing-monitor-empty')?.classList.contains('d-none')).toBe(false);
    });

    it('should relay click to the main playlist button behavior via simulateClick', async () => {
        const sourceBtn = setupDOM('playlist-dim-100', false);
        const simulateClick = vi.fn();
        vi.mocked(ButtonPlaylistFinder.search).mockReturnValue({ simulateClick } as any);
        const monitor = new PlayingMonitor();

        monitor.init();
        sourceBtn.classList.add('active-playlist');
        await flushMutationObservers();

        const stopBtn = document.querySelector('.playing-monitor-stop-btn') as HTMLElement;
        stopBtn.click();

        expect(ButtonPlaylistFinder.search).toHaveBeenCalledWith('abc');
        expect(simulateClick).toHaveBeenCalledTimes(1);
    });

    it('should be idempotent when init is called twice', async () => {
        const sourceBtn = setupDOM('playlist-dim-100', false);
        const monitor = new PlayingMonitor();

        monitor.init();
        monitor.init();

        sourceBtn.classList.add('active-playlist');
        await flushMutationObservers();

        expect(document.querySelectorAll('.playing-monitor-stop-btn')).toHaveLength(1);
    });

    it('should stop reacting after destroy is called', async () => {
        const sourceBtn = setupDOM('playlist-dim-100', false);
        const monitor = new PlayingMonitor();

        monitor.init();
        monitor.destroy();

        sourceBtn.classList.add('active-playlist');
        await flushMutationObservers();

        expect(document.querySelectorAll('.playing-monitor-stop-btn')).toHaveLength(0);
    });
});
