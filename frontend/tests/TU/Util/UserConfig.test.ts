import { describe, it, expect, afterEach } from 'vitest';
import UserConfig from '../../../src/modules/Util/UserConfig';

function setTouchDevice(hasTouch: boolean) {
    if (hasTouch) {
        Object.defineProperty(globalThis, 'ontouchstart', { value: () => {}, configurable: true });
    } else {
        // @ts-ignore
        delete globalThis.ontouchstart;
    }
    Object.defineProperty(navigator, 'maxTouchPoints', { value: hasTouch ? 5 : 0, configurable: true });
}

function setCoarsePointer(isCoarse: boolean) {
    globalThis.matchMedia = ((query: string) => ({
        matches: isCoarse,
        media: query,
        onchange: null,
        addListener: () => {},
        removeListener: () => {},
        addEventListener: () => {},
        removeEventListener: () => {},
        dispatchEvent: () => false,
    })) as unknown as typeof globalThis.matchMedia;
}

describe('UserConfig.detectKeyboard', () => {
    afterEach(() => {
        // @ts-ignore
        delete globalThis.ontouchstart;
        Object.defineProperty(navigator, 'maxTouchPoints', { value: 0, configurable: true });
    });

    it('should return false for a touch device with a coarse pointer', () => {
        setTouchDevice(true);
        setCoarsePointer(true);
        expect(UserConfig.detectKeyboard()).toBe(false);
    });

    it('should return true for a touch device without a coarse pointer', () => {
        setTouchDevice(true);
        setCoarsePointer(false);
        expect(UserConfig.detectKeyboard()).toBe(true);
    });

    it('should return true for a non touch device', () => {
        setTouchDevice(false);
        setCoarsePointer(false);
        expect(UserConfig.detectKeyboard()).toBe(true);
    });
});
