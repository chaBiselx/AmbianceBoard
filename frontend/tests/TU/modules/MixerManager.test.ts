import { beforeEach, describe, expect, it, vi } from 'vitest';
import { MixerManager } from '@/modules/MixerManager';
import { MixerElement } from '@/modules/MixerElement';

const mixerManagerMocks = vi.hoisted(() => ({
    isSlavePage: vi.fn(),
    getMasterInstance: vi.fn(),
    sendMessage: vi.fn(),
    fromAudioElement: vi.fn(),
    clearCache: vi.fn(),
    update: vi.fn(),
}));

vi.mock('@/modules/SharedSoundBoardUtil', () => ({
    default: { isSlavePage: mixerManagerMocks.isSlavePage },
}));

vi.mock('@/modules/SharedSoundBoardWebSocket', () => ({
    default: { getMasterInstance: mixerManagerMocks.getMasterInstance },
}));

vi.mock('@/modules/MusicElementFactory', () => ({
    MusicElementFactory: { fromAudioElement: mixerManagerMocks.fromAudioElement },
}));

vi.mock('@/modules/UpdateVolumeElement', () => ({
    default: class {
        clearCache(type: string) {
            mixerManagerMocks.clearCache(type);
            return this;
        }

        update() {
            mixerManagerMocks.update();
        }
    },
}));

describe('MixerManager', () => {
    beforeEach(() => {
        vi.clearAllMocks();
        mixerManagerMocks.isSlavePage.mockReturnValue(false);
        mixerManagerMocks.getMasterInstance.mockReturnValue({ sendMessage: mixerManagerMocks.sendMessage });
        document.body.innerHTML = '';
    });

    it('registers each slider only once, including when initialization is repeated', () => {
        document.body.innerHTML = `
            <input class="mixer-playlist" id="mixer-music" data-type="music" value="0.6">
            <audio class="audio-music"></audio>
        `;
        const slider = document.querySelector<HTMLInputElement>('.mixer-playlist')!;
        mixerManagerMocks.fromAudioElement.mockReturnValue({});

        new MixerManager().initializeEventListeners();
        new MixerManager().initializeEventListeners();
        slider.dispatchEvent(new Event('input'));

        expect(mixerManagerMocks.getMasterInstance).toHaveBeenCalledOnce();
        expect(mixerManagerMocks.sendMessage).toHaveBeenCalledOnce();
        expect(mixerManagerMocks.sendMessage).toHaveBeenCalledWith({
            type: 'send_mixer_update',
            data: { type: 'music', value: 0.6 },
        });
        expect(mixerManagerMocks.clearCache).toHaveBeenCalledOnce();
        expect(mixerManagerMocks.update).toHaveBeenCalledOnce();
    });

    it('registers sliders added after the initial setup and applies general changes to every type', () => {
        document.body.innerHTML = `
            <input class="mixer-playlist" id="mixer-general" data-type="General" value="0.75">
            <input class="mixer-playlist mixer-playlist-type" id="mixer-music" data-type="music" value="0.6">
            <input class="mixer-playlist mixer-playlist-type" id="mixer-ambience" data-type="ambience" value="0.4">
            <audio class="audio-music"></audio>
            <audio class="audio-ambience"></audio>
        `;
        const manager = new MixerManager();
        manager.initializeEventListeners();
        const newSlider = document.createElement('input');
        newSlider.className = 'mixer-playlist';
        newSlider.id = 'mixer-effects';
        newSlider.dataset.type = 'effects';
        newSlider.value = '0.3';
        document.body.appendChild(newSlider);
        manager.initializeEventListeners();
        mixerManagerMocks.fromAudioElement.mockReturnValue({});

        newSlider.dispatchEvent(new Event('input'));
        document.getElementById('mixer-general')!.dispatchEvent(new Event('input'));

        expect(mixerManagerMocks.sendMessage).toHaveBeenNthCalledWith(1, {
            type: 'send_mixer_update',
            data: { type: 'effects', value: 0.3 },
        });
        expect(mixerManagerMocks.sendMessage).toHaveBeenNthCalledWith(2, {
            type: 'send_mixer_update',
            data: { type: 'General', value: 0.75 },
        });
        expect(mixerManagerMocks.clearCache.mock.calls.map(([type]) => type)).toEqual(['music', 'ambience']);
    });

    it('applies a remote value through the same mixer input event', () => {
        document.body.innerHTML = `
            <input class="mixer-playlist" id="mixer-music" data-type="music" value="0.6">
            <audio class="audio-music"></audio>
        `;
        mixerManagerMocks.fromAudioElement.mockReturnValue({});
        new MixerManager().initializeEventListeners();

        new MixerElement('music').update(0.25);

        expect(document.querySelector<HTMLInputElement>('.mixer-playlist')!.value).toBe('0.25');
        expect(mixerManagerMocks.sendMessage).toHaveBeenCalledOnce();
        expect(mixerManagerMocks.sendMessage).toHaveBeenCalledWith({
            type: 'send_mixer_update',
            data: { type: 'music', value: 0.25 },
        });
    });
});
