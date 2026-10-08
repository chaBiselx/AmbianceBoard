import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { Collapse } from 'bootstrap';
import SoundboardEditMode from '@/modules/SoundBoardEditor/SoundboardEditMode';

const previewMocks = vi.hoisted(() => ({ notify: vi.fn(), show: vi.fn(), hide: vi.fn() }));
vi.mock('@/modules/General/Csrf', () => ({ default: { getToken: () => 'csrf-token' } }));
vi.mock('@/modules/General/Notifications', () => ({ default: { createClientNotification: previewMocks.notify } }));
vi.mock('@/modules/General/Modal', () => ({
    default: { show: previewMocks.show, getInstance: () => ({ hide: previewMocks.hide }) },
}));
vi.mock('@/modules/SoundBoardEditor/PopupAddMusicToSoundboard', () => ({ default: class { showIfValue() {} } }));
vi.mock('@/modules/SoundBoardEventListener', () => ({ default: class { addEventListenerDom() {} } }));
vi.mock('@/modules/MixerManager', () => ({
    MixerManager: class {
        initializeEventListeners() {}
        static updatePlaylistVolumeWidths() {}
    },
}));

const communityMarkup = (page = 'initial') => `
    <select name="genre" data-edit-mode-filter="true"><option value="">All</option><option value="ambient">Ambient</option></select>
    <div id="pagination"><li class="page-item"><button class="page-link" data-page="2">2</button></li></div>
    <button class="btn-edit-mode-duplicate" data-url-duplication="/duplicate">Copy</button>
    ${['first', 'second'].map(name => `
        <button type="button" class="collapsed" data-bs-toggle="collapse" data-bs-target="#tracks-${name}" aria-expanded="false">Sounds</button>
        <div id="tracks-${name}" class="collapse community-track-list">
            <div class="player-custom" data-url="/stream/${page}/${name}"><audio preload="none"></audio></div>
        </div>
    `).join('')}
`;

const htmlResponse = (body: string) => ({ ok: true, redirected: false, text: async () => body }) as Response;
const configureAudio = (audio: HTMLAudioElement) => {
    let paused = true;
    Object.defineProperty(audio, 'paused', { configurable: true, get: () => paused });
    audio.play = vi.fn(() => { paused = false; return Promise.resolve(); });
    audio.pause = vi.fn(() => { paused = true; });
    audio.load = vi.fn();
    return audio;
};

describe('SoundboardEditModePreview', () => {
    let fetchMock: ReturnType<typeof vi.fn>;

    beforeEach(() => {
        vi.clearAllMocks();
        vi.spyOn(HTMLMediaElement.prototype, 'pause').mockImplementation(() => {});
        vi.spyOn(HTMLMediaElement.prototype, 'load').mockImplementation(() => {});
        document.body.innerHTML = `
            <section class="responsive-sections-container" data-soundboard-editable="true">
                <div class="flex-container"><a class="playlist-link">Existing</a>
                    <button class="soundboard-edit-add-zone" data-soundboard-edit-open-panel="true">Add</button>
                </div>
                <audio id="soundboard-audio"></audio>
            </section>
            <button id="btn-soundboard-edit-mode" data-url-panel="/panel"></button>
            <div id="mainModal"><div id="mainModalBody"></div></div>
        `;
        previewMocks.show.mockImplementation((options: { body: string; callback: () => void }) => {
            document.getElementById('mainModalBody')!.innerHTML = options.body;
            options.callback();
        });
        previewMocks.hide.mockImplementation(() => {
            document.getElementById('mainModal')!.dispatchEvent(new Event('hide.bs.modal'));
        });
        fetchMock = vi.fn(async (input: RequestInfo | URL) => {
            const url = new URL(String(input), globalThis.location.origin);
            if (url.pathname === '/panel') return htmlResponse(`
                <button id="community-tab">Community</button>
                <div id="soundboard-edit-playlist-list-container" data-url-list="/community"></div>
                <div id="soundboard-edit-my-playlist-list-container" data-url-list="/mine"></div>
            `);
            if (url.pathname === '/community') return htmlResponse(communityMarkup(url.searchParams.get('page') || '1'));
            if (url.pathname === '/mine') return htmlResponse('<div class="player-custom" data-url="/mine-audio"><audio></audio></div>');
            if (url.pathname === '/duplicate') return { ok: true, json: async () => ({ success: true }) } as Response;
            throw new Error(`Unexpected request: ${url.pathname}`);
        });
        vi.stubGlobal('fetch', fetchMock);
        vi.stubGlobal('WebSocket', vi.fn());
    });

    afterEach(() => {
        document.getElementById('mainModal')?.dispatchEvent(new Event('hide.bs.modal'));
        vi.restoreAllMocks();
        vi.unstubAllGlobals();
    });

    const openPreview = async () => {
        new SoundboardEditMode().addEvent();
        document.getElementById('btn-soundboard-edit-mode')!.click();
        document.querySelector<HTMLButtonElement>('.soundboard-edit-add-zone')!.click();
        await vi.waitFor(() => expect(document.querySelectorAll('#soundboard-edit-playlist-list-container .btn-play')).toHaveLength(2));
        return Array.from(document.querySelectorAll<HTMLAudioElement>('#soundboard-edit-playlist-list-container audio')).map(configureAudio);
    };

    const playButton = (name = 'first') => document.querySelector<HTMLButtonElement>(`#tracks-${name} .btn-play`)!;

    it('loads audio only on play and coordinates previews without affecting soundboard audio or WebSocket', async () => {
        const [first, second] = await openPreview();
        const boardAudio = configureAudio(document.getElementById('soundboard-audio') as HTMLAudioElement);
        await boardAudio.play();
        expect(first.hasAttribute('src')).toBe(false);
        expect(second.hasAttribute('src')).toBe(false);
        expect(document.querySelectorAll('.community-track-list.show')).toHaveLength(0);
        expect(document.querySelector('#soundboard-edit-my-playlist-list-container .btn-play')).toBeNull();
        playButton().click();
        first.currentTime = 15;
        playButton('second').click();
        expect(first.paused).toBe(true);
        expect(first.currentTime).toBe(0);
        expect(second.paused).toBe(false);
        document.querySelector<HTMLButtonElement>('#tracks-first .btn-reload')!.click();
        expect(second.paused).toBe(true);
        expect(first.paused).toBe(false);
        expect(boardAudio.pause).not.toHaveBeenCalled();
        expect(WebSocket).not.toHaveBeenCalled();
    });

    it('stops playback immediately when Bootstrap collapses the active list', async () => {
        const [first] = await openPreview();
        const list = document.getElementById('tracks-first')!;
        const collapse = new Collapse(list, { toggle: false });
        collapse.show();
        await vi.waitFor(() => expect(list.classList.contains('show')).toBe(true));
        playButton().click();
        collapse.hide();
        expect(first.paused).toBe(true);
        expect(first.currentTime).toBe(0);
        await vi.waitFor(() => expect(list.classList.contains('collapse')).toBe(true));
        collapse.dispose();
    });

    it.each(['hide.bs.tab', 'hide.bs.modal'])('stops playback on %s and removes modal audio on close', async (eventName) => {
        const [first] = await openPreview();
        const button = playButton();
        button.click();
        const target = eventName === 'hide.bs.tab' ? document.getElementById('community-tab')! : document.getElementById('mainModal')!;
        target.dispatchEvent(new Event(eventName, { bubbles: true }));
        expect(first.paused).toBe(true);
        expect(first.currentTime).toBe(0);
        if (eventName === 'hide.bs.modal') {
            expect(first.hasAttribute('src')).toBe(false);
            button.click();
            expect(first.play).toHaveBeenCalledOnce();
        }
    });

    it('stops and disposes old audio when paginating or filtering, without duplicate controls', async () => {
        const [first] = await openPreview();
        const oldButton = playButton();
        oldButton.click();
        document.querySelector<HTMLButtonElement>('.page-link')!.click();
        expect(first.paused).toBe(true);
        await vi.waitFor(() => expect(document.querySelector('#tracks-first .player-custom')?.getAttribute('data-url')).toBe('/stream/2/first'));
        expect(first.hasAttribute('src')).toBe(false);
        oldButton.click();
        expect(first.play).toHaveBeenCalledOnce();
        const next = configureAudio(document.querySelector<HTMLAudioElement>('#tracks-first audio')!);
        playButton().click();
        const filter = document.querySelector<HTMLSelectElement>('[data-edit-mode-filter]')!;
        filter.value = 'ambient';
        filter.dispatchEvent(new Event('change'));
        expect(next.paused).toBe(true);
        await vi.waitFor(() => expect(document.querySelector('#tracks-first .player-custom')?.getAttribute('data-url')).toBe('/stream/1/first'));
        expect(next.hasAttribute('src')).toBe(false);
        expect(document.querySelectorAll('#soundboard-edit-playlist-list-container .player-custom-container')).toHaveLength(2);
    });

    it('ignores an outstanding page response after closing the modal', async () => {
        const [first] = await openPreview();
        let resolvePage!: (response: Response) => void;
        fetchMock.mockImplementationOnce(() => new Promise<Response>(resolve => { resolvePage = resolve; }));
        playButton().click();
        document.querySelector<HTMLButtonElement>('.page-link')!.click();
        previewMocks.hide();
        resolvePage(htmlResponse(communityMarkup('late')));
        await vi.waitFor(() => expect(first.hasAttribute('src')).toBe(false));
        await new Promise<void>(resolve => queueMicrotask(resolve));
        expect(document.querySelectorAll('.player-custom-container')).toHaveLength(0);
        expect(document.querySelector('[data-url="/stream/late/first"]')).toBeNull();
    });

    it('ignores an older page response after newer filters have loaded', async () => {
        await openPreview();
        let resolvePage!: (response: Response) => void;
        fetchMock.mockImplementationOnce(() => new Promise<Response>(resolve => { resolvePage = resolve; }));
        document.querySelector<HTMLButtonElement>('.page-link')!.click();
        const filter = document.querySelector<HTMLSelectElement>('[data-edit-mode-filter]')!;
        filter.value = 'ambient';
        filter.dispatchEvent(new Event('change'));
        await vi.waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(5));
        await vi.waitFor(() => expect(document.querySelectorAll('.player-custom-container')).toHaveLength(2));
        resolvePage(htmlResponse(communityMarkup('stale')));
        await new Promise<void>(resolve => queueMicrotask(resolve));
        expect(document.querySelector('[data-url="/stream/stale/first"]')).toBeNull();
    });

    it('stops preview when copying a playlist and cleans up on successful close', async () => {
        const [first] = await openPreview();
        playButton().click();
        document.querySelector<HTMLButtonElement>('.btn-edit-mode-duplicate')!.click();
        expect(first.paused).toBe(true);
        await vi.waitFor(() => expect(previewMocks.hide).toHaveBeenCalledOnce());
        expect(first.hasAttribute('src')).toBe(false);
    });

    it('does not insert a redirected login page into the playlist list', async () => {
        const [first] = await openPreview();
        fetchMock.mockResolvedValueOnce({ redirected: true, text: async () => '<form id="login">Login</form>' } as Response);
        playButton().click();
        document.querySelector<HTMLButtonElement>('.page-link')!.click();
        await vi.waitFor(() => expect(previewMocks.notify).toHaveBeenCalledWith(expect.objectContaining({ type: 'danger' })));
        expect(first.paused).toBe(true);
        expect(document.getElementById('login')).toBeNull();
    });
});