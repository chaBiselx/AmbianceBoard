import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import AudioFadeManager from '@/modules/AudioFadeManager';
import type { MusicElement } from '@/modules/MusicElement';

const fadeMocks = vi.hoisted(() => ({ update: vi.fn() }));

vi.mock('@/modules/UpdateVolumeElement', () => ({
    default: class {
        update() {
            fadeMocks.update();
        }
    },
}));

describe('AudioFadeManager', () => {
    let musicElement: MusicElement;

    beforeEach(() => {
        vi.useFakeTimers();
        vi.setSystemTime(0);
        vi.clearAllMocks();
        musicElement = { levelFade: 1 } as MusicElement;
    });

    afterEach(() => {
        vi.useRealTimers();
    });

    it('updates volume through a fade and completes at the target level', () => {
        const onComplete = vi.fn();
        const manager = new AudioFadeManager(musicElement, undefined, true, onComplete);
        manager.setDuration(0.4);

        expect(musicElement.levelFade).toBe(0);
        manager.start();
        vi.advanceTimersByTime(200);

        expect(musicElement.levelFade).toBe(0.5);
        vi.advanceTimersByTime(200);

        expect(musicElement.levelFade).toBe(1);
        expect(onComplete).toHaveBeenCalledOnce();
        expect(fadeMocks.update).toHaveBeenCalledTimes(3);
    });

    it('can skip a fade out and call its completion callback', () => {
        const onComplete = vi.fn();
        const manager = new AudioFadeManager(musicElement, undefined, false, onComplete);

        manager.skip();

        expect(musicElement.levelFade).toBe(0);
        expect(onComplete).toHaveBeenCalledOnce();
        expect(fadeMocks.update).toHaveBeenCalledTimes(2);
    });
});