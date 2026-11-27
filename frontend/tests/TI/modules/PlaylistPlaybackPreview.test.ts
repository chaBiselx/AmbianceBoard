import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { PlaylistPlaybackPreview } from '@/modules/Form/PlaylistPlaybackPreview';
import { MusicElement } from '@/modules/MusicElement';

const shared = vi.hoisted(() => ({ send: vi.fn() }));
vi.mock('@/modules/SharedSoundBoardWebSocket', () => ({ default: { getMasterInstance: () => ({ sendMessage: shared.send }) } }));

describe('PlaylistPlaybackPreview integration', () => {
    let preview: PlaylistPlaybackPreview;
    let tile: HTMLButtonElement;

    beforeEach(() => {
        vi.useFakeTimers();
        vi.clearAllMocks();
        vi.spyOn(HTMLMediaElement.prototype, 'play').mockResolvedValue(undefined);
        vi.spyOn(HTMLMediaElement.prototype, 'pause').mockImplementation(() => {});
        vi.spyOn(HTMLMediaElement.prototype, 'load').mockImplementation(() => {});
        vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: true, json: async () => ({ name: 'Playing track', duration: 100 }) }));
        document.cookie = 'WebSocketToken="leftover-shared-session"';
        document.body.innerHTML = `<div data-playlist-playback-preview data-idle="Stopped" data-waiting="Waiting" data-error="Error">
            <button type="button" class="playlist-link" id="playlist-one" data-playlist-id="one" data-playlist-type="music"
                data-playlist-preview="true" data-playlist-uri="/preview/stream" data-playlist-volume="75" data-playlist-loop="true"
                data-playlist-durationremainingtriggernextmusic="2" data-playlist-fadeintype="disabled" data-playlist-fadeouttype="disabled"
                data-playlist-fadeoffonstoptype="disabled"></button>
            <div data-preview-status></div><div data-preview-tracks></div><div id="players"></div>
            <input id="playlist-preview-volume" type="range" min="0" max="100" value="75"><output data-preview-volume-value></output>
        </div>`;
        tile = document.getElementById('playlist-one') as HTMLButtonElement;
        preview = new PlaylistPlaybackPreview(document.querySelector('[data-playlist-playback-preview]')!);
    });

    afterEach(() => {
        preview.destroy();
        document.cookie = 'WebSocketToken=; Max-Age=0';
        vi.restoreAllMocks();
        vi.unstubAllGlobals();
        vi.useRealTimers();
    });

    function currentAudio(): HTMLAudioElement {
        return document.querySelector<HTMLAudioElement>('#players audio')!;
    }

    function finishTrack(audio: HTMLAudioElement): void {
        Object.defineProperty(audio, 'duration', { value: 100, configurable: true });
        audio.currentTime = 99;
        audio.dispatchEvent(new Event('loadedmetadata'));
        audio.dispatchEvent(new Event('timeupdate'));
        audio.dispatchEvent(new Event('ended'));
    }

    it('uses the real soundboard engine, displays metadata and keeps mute across tracks without sharing', async () => {
        expect(currentAudio()).toBeNull();
        tile.click();
        const audio = currentAudio();
        expect(audio.src).toContain('/preview/stream?i=');
        audio.currentTime = 12;
        audio.dispatchEvent(new Event('playing'));
        await vi.advanceTimersByTimeAsync(750);
        expect(document.querySelector('[data-preview-tracks]')!.textContent).toContain('Playing track0:12 / 1:40');
        const volume = document.getElementById('playlist-preview-volume') as HTMLInputElement;
        volume.value = '0';
        volume.dispatchEvent(new Event('input'));
        expect(audio.volume).toBe(0);
        finishTrack(audio);
        await vi.advanceTimersByTimeAsync(35);
        expect(currentAudio()).not.toBe(audio);
        expect(currentAudio().volume).toBe(0);
        expect(shared.send).not.toHaveBeenCalled();
        preview.destroy();
        await vi.advanceTimersByTimeAsync(10000);
        expect(currentAudio()).toBeNull();
        expect(MusicElement.getPreviewElements()).toEqual([]);
        expect(vi.getTimerCount()).toBe(0);
    });

    it('stops the original instance on a second click and supports a clean restart', async () => {
        tile.click();
        tile.click();
        await vi.advanceTimersByTimeAsync(250);
        expect(MusicElement.getPreviewElements()).toEqual([]);
        expect(currentAudio()).toBeNull();
        expect(document.querySelector('[data-preview-status]')!.textContent).toBe('Stopped');
        tile.click();
        expect(currentAudio()).not.toBeNull();
        expect(MusicElement.getPreviewElements()).toHaveLength(1);
    });

    it('cancels a pending loop delay when closed', async () => {
        vi.spyOn(Math, 'random').mockReturnValue(0.5);
        tile.dataset.playlistDelay = '5';
        tile.click();
        finishTrack(currentAudio());
        await vi.advanceTimersByTimeAsync(35);
        expect(currentAudio()).toBeNull();
        preview.destroy();
        await vi.advanceTimersByTimeAsync(10000);
        expect(currentAudio()).toBeNull();
        expect(vi.getTimerCount()).toBe(0);
    });

    it('cancels active fades and metadata work when closed', async () => {
        tile.dataset.playlistFadeintype = 'linear';
        tile.dataset.playlistFadeinduration = '1';
        tile.click();
        const audio = currentAudio();
        Object.defineProperty(audio, 'duration', { value: 100 });
        Object.defineProperty(audio, 'readyState', { value: 2 });
        audio.dispatchEvent(new Event('playing'));
        await vi.advanceTimersByTimeAsync(200);
        expect(audio.volume).toBeGreaterThan(0);
        const clearIntervalSpy = vi.spyOn(globalThis, 'clearInterval');
        const clearTimeoutSpy = vi.spyOn(globalThis, 'clearTimeout');
        preview.destroy();
        expect(clearIntervalSpy).toHaveBeenCalled();
        expect(clearTimeoutSpy).toHaveBeenCalled();
        await vi.advanceTimersByTimeAsync(600);
        expect(vi.getTimerCount()).toBe(0);
        expect(audio.getAttribute('src')).toBeNull();
        expect(shared.send).not.toHaveBeenCalled();
    });
});