import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import WakeLock from '../../../src/modules/General/WakeLock';
import Config from '../../../src/modules/General/Config';

vi.mock('@/modules/General/Config', () => ({
    default: { DEBUG: false, SOUNDBOARD_DIV_ID_PLAYERS: 'players' },
}));

function createSentinel() {
    const listeners: Record<string, Array<() => void>> = {};
    return {
        addEventListener: vi.fn((event: string, callback: () => void) => {
            listeners[event] = listeners[event] || [];
            listeners[event].push(callback);
        }),
        release: vi.fn(),
        emit(event: string) {
            (listeners[event] || []).forEach((callback) => callback());
        },
    };
}

describe('WakeLock', () => {
    let requestMock: ReturnType<typeof vi.fn>;

    beforeEach(() => {
        requestMock = vi.fn();
        Object.defineProperty(navigator, 'wakeLock', {
            value: { request: requestMock },
            configurable: true,
        });
        Object.defineProperty(document, 'visibilityState', { value: 'visible', configurable: true });
        (Config as any).DEBUG = false;
    });

    afterEach(() => {
        vi.restoreAllMocks();
    });

    it('should acquire the wake lock and log when DEBUG is enabled', async () => {
        (Config as any).DEBUG = true;
        const sentinel = createSentinel();
        requestMock.mockResolvedValue(sentinel);
        const logSpy = vi.spyOn(console, 'log').mockImplementation(() => {});

        const wakeLock = new WakeLock();
        await wakeLock.start();

        expect(requestMock).toHaveBeenCalledWith('screen');
        expect(logSpy).toHaveBeenCalledWith('Wake Lock activé !');
    });

    it('should acquire the wake lock without logging when DEBUG is disabled', async () => {
        const sentinel = createSentinel();
        requestMock.mockResolvedValue(sentinel);
        const logSpy = vi.spyOn(console, 'log').mockImplementation(() => {});

        const wakeLock = new WakeLock();
        await wakeLock.start();

        expect(logSpy).not.toHaveBeenCalled();
    });

    it('should reset the wake lock and log when it is released and DEBUG is enabled', async () => {
        (Config as any).DEBUG = true;
        const sentinel = createSentinel();
        requestMock.mockResolvedValue(sentinel);
        const logSpy = vi.spyOn(console, 'log').mockImplementation(() => {});

        const wakeLock = new WakeLock();
        await wakeLock.start();
        logSpy.mockClear();
        sentinel.emit('release');

        expect(logSpy).toHaveBeenCalledWith('Wake Lock relâché');
        wakeLock.stop();
    });

    it('should reset the wake lock without logging when it is released and DEBUG is disabled', async () => {
        const sentinel = createSentinel();
        requestMock.mockResolvedValue(sentinel);
        const logSpy = vi.spyOn(console, 'log').mockImplementation(() => {});

        const wakeLock = new WakeLock();
        await wakeLock.start();
        logSpy.mockClear();
        sentinel.emit('release');

        expect(logSpy).not.toHaveBeenCalled();
        wakeLock.stop();
    });

    it('should log the error when the request fails and DEBUG is enabled', async () => {
        (Config as any).DEBUG = true;
        requestMock.mockRejectedValue(new Error('denied'));
        const errorSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

        await new WakeLock().start();

        expect(errorSpy).toHaveBeenCalledWith('Erreur avec Wake Lock: denied');
    });

    it('should not log the error when the request fails and DEBUG is disabled', async () => {
        requestMock.mockRejectedValue(new Error('denied'));
        const errorSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

        await new WakeLock().start();

        expect(errorSpy).not.toHaveBeenCalled();
    });

    it('should release the wake lock on stop', async () => {
        const sentinel = createSentinel();
        requestMock.mockResolvedValue(sentinel);

        const wakeLock = new WakeLock();
        await wakeLock.start();
        wakeLock.stop();

        expect(sentinel.release).toHaveBeenCalled();
    });

    it('should do nothing on stop when there is no active wake lock', () => {
        expect(() => new WakeLock().stop()).not.toThrow();
    });

    it('should re-acquire the wake lock when the page becomes visible again', async () => {
        const sentinel = createSentinel();
        requestMock.mockResolvedValue(sentinel);

        const wakeLock = new WakeLock();
        await wakeLock.start();
        requestMock.mockClear();

        // Invoke the private handler directly to avoid leaking document-level
        // listeners from other WakeLock instances created in other tests.
        await (wakeLock as any).handleVisibilityChange();

        expect(requestMock).toHaveBeenCalled();
    });

    it('should not re-acquire the wake lock when there is none active', async () => {
        const wakeLock = new WakeLock();
        requestMock.mockClear();

        await (wakeLock as any).handleVisibilityChange();

        expect(requestMock).not.toHaveBeenCalled();
    });
});
