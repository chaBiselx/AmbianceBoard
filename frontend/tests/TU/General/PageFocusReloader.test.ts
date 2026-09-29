import { describe, it, expect, vi, afterEach } from 'vitest';
import PageFocusReloader from '../../../src/modules/General/PageFocusReloader';

describe('PageFocusReloader', () => {
    afterEach(() => {
        vi.restoreAllMocks();
    });

    it('reloads the page when the window regains focus', () => {
        const reloadSpy = vi.fn();
        Object.defineProperty(globalThis, 'location', {
            value: { ...globalThis.location, reload: reloadSpy },
            configurable: true,
            writable: true,
        });

        new PageFocusReloader().setupFocusListener();
        window.dispatchEvent(new Event('focus'));

        expect(reloadSpy).toHaveBeenCalledTimes(1);
    });
});
