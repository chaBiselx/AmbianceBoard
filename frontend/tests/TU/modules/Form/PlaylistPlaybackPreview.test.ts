import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { initializePlaylistPlaybackPreview, PlaylistPlaybackPreview } from '@/modules/Form/PlaylistPlaybackPreview';

const mocks = vi.hoisted(() => ({ add: vi.fn(), remove: vi.fn(), dispose: vi.fn(), elements: [] as any[] }));
vi.mock('@/modules/SoundBoardManager', () => ({ SoundBoardManager: { addPlaylist: mocks.add, removePlaylist: mocks.remove } }));
vi.mock('@/modules/MusicElement', () => ({ MusicElement: { getPreviewElements: () => mocks.elements, disposePreview: mocks.dispose } }));
vi.mock('@/modules/UpdateVolumeElement', () => ({ default: class { update() {} } }));

const body = `<div data-playlist-playback-preview data-idle="Stopped" data-waiting="Waiting" data-error="Error">
    <button id="playlist-one" data-playlist-id="one" data-playlist-type="music" data-playlist-preview="true" data-playlist-volume="75"></button>
    <div data-preview-status></div><div data-preview-tracks></div>
    <input id="playlist-preview-volume" type="range" min="0" max="100" value="75"><output data-preview-volume-value></output>
</div>`;

describe('PlaylistPlaybackPreview', () => {
    let preview: PlaylistPlaybackPreview | null;

    beforeEach(() => {
        vi.clearAllMocks();
        vi.useFakeTimers();
        mocks.elements = [];
        preview = null;
        document.body.innerHTML = `<button id="btn-test-playlist" data-url="/preview" data-modal-title="Test" data-error="Unavailable"></button>
            <div id="mainModal"><div id="mainModalBody">${body}</div></div>`;
    });

    afterEach(() => {
        preview?.destroy();
        window.dispatchEvent(new Event('pagehide'));
        vi.useRealTimers();
    });

    it('does not autoplay, toggles the soundboard button and disposes playback', () => {
        preview = new PlaylistPlaybackPreview(document.querySelector('[data-playlist-playback-preview]')!);
        expect(mocks.add).not.toHaveBeenCalled();
        const tile = document.getElementById('playlist-one')!;
        tile.click();
        expect(mocks.add).toHaveBeenCalledOnce();
        expect(tile.getAttribute('aria-pressed')).toBe('true');
        tile.click();
        expect(mocks.remove).toHaveBeenCalledOnce();
        preview.destroy();
        expect(mocks.dispose).toHaveBeenCalledOnce();
    });

    it('shows each audible track safely and keeps volume changes local, including mute', () => {
        const element = { getPlaybackState: () => ({ name: '<img src=x>', currentTime: 65, duration: 125 }), setDefaultVolume: vi.fn() };
        mocks.elements = [element, { ...element, getPlaybackState: () => ({ name: 'Next', currentTime: 1, duration: Infinity }) }];
        preview = new PlaylistPlaybackPreview(document.querySelector('[data-playlist-playback-preview]')!);
        expect(document.querySelector('[data-preview-tracks]')!.textContent).toContain('<img src=x>1:05 / 2:05');
        expect(document.querySelector('[data-preview-tracks]')!.textContent).toContain('Next0:01 / --:--');
        expect(document.querySelector('img')).toBeNull();
        const volume = document.getElementById('playlist-preview-volume') as HTMLInputElement;
        volume.value = '0';
        volume.dispatchEvent(new Event('input'));
        expect(element.setDefaultVolume).toHaveBeenCalledWith(0);
        expect(document.querySelector('output')!.value).toBe('0 %');
        expect(document.getElementById('playlist-one')!.dataset.playlistVolume).toBe('0');
    });

    it('loads the saved modal and stops playback when it closes', async () => {
        const fetch = vi.fn().mockResolvedValue({ ok: true, text: async () => body });
        const showModal = vi.fn(options => { document.getElementById('mainModalBody')!.innerHTML = options.body; options.callback(); });
        initializePlaylistPlaybackPreview({ fetch, showModal, notify: vi.fn() });
        document.getElementById('btn-test-playlist')!.click();
        await vi.advanceTimersByTimeAsync(0);
        expect(fetch).toHaveBeenCalledWith('/preview', expect.objectContaining({ signal: expect.any(AbortSignal) }));
        expect(showModal).toHaveBeenCalledOnce();
        document.getElementById('mainModal')!.dispatchEvent(new Event('hide.bs.modal'));
        expect(mocks.dispose).toHaveBeenCalledOnce();
    });

    it('ignores a late modal response after navigation', async () => {
        let resolve!: (response: unknown) => void;
        const fetch = vi.fn(() => new Promise(resolveResponse => { resolve = resolveResponse; })) as unknown as typeof globalThis.fetch;
        const showModal = vi.fn();
        initializePlaylistPlaybackPreview({ fetch, showModal, notify: vi.fn() });
        document.getElementById('btn-test-playlist')!.click();
        window.dispatchEvent(new Event('pagehide'));
        resolve({ ok: true, text: async () => body });
        await vi.advanceTimersByTimeAsync(0);
        expect(showModal).not.toHaveBeenCalled();
    });
});