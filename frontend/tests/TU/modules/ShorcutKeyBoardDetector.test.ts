import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import ShorcutKeyBoardDetector from '@/modules/Control/ShorcutKeyBoardDetector';

describe('ShorcutKeyBoardDetector', () => {
    let detector: ShorcutKeyBoardDetector;

    const dispatchKey = (type: 'keydown' | 'keyup', key: string, options: KeyboardEventInit = {}) => {
        const event = new KeyboardEvent(type, { key, bubbles: true, cancelable: true, ...options });
        const stopPropagation = vi.spyOn(event, 'stopPropagation');
        document.dispatchEvent(event);
        return { event, stopPropagation };
    };

    beforeEach(() => {
        detector = new ShorcutKeyBoardDetector();
    });

    afterEach(() => {
        detector.stopListening();
    });

    it('registers key listeners once and removes them when stopped', () => {
        const callback = vi.fn(() => true);
        detector.startListening(callback);
        detector.startListening(vi.fn(() => true));

        dispatchKey('keydown', 'a');
        expect(callback).toHaveBeenCalledTimes(1);

        detector.stopListening();
        dispatchKey('keydown', 'b');

        expect(callback).toHaveBeenCalledTimes(1);
        expect(detector.getPressedKeys()).toEqual([]);
    });

    it('ignores modifier-only keys and builds normalized shortcuts', () => {
        const callback = vi.fn(() => true);
        detector.startListening(callback);

        dispatchKey('keydown', 'Control');
        expect(callback).not.toHaveBeenCalled();
        expect(detector.getPressedKeys()).toEqual(['Ctrl']);

        dispatchKey('keydown', 'a', {
            ctrlKey: true,
            altKey: true,
            shiftKey: true,
            metaKey: true,
        });

        expect(callback).toHaveBeenCalledWith(['Ctrl', 'Alt', 'Shift', 'Cmd', 'a']);
    });

    it('normalizes Meta and the space key in the pressed-key list', () => {
        detector.startListening(() => true);

        dispatchKey('keydown', 'Meta');
        dispatchKey('keydown', ' ');

        expect(detector.getPressedKeys()).toEqual(['Cmd', 'Space']);
    });

    it('prevents the default action only when the callback returns false', () => {
        detector.startListening(() => false);

        const { event } = dispatchKey('keydown', 'a');

        expect(event.defaultPrevented).toBe(true);
    });

    it('does not prevent the default action when the callback returns true', () => {
        detector.startListening(() => true);

        const { event } = dispatchKey('keydown', 'a');

        expect(event.defaultPrevented).toBe(false);
    });

    it('does not handle a held key again until its keyup event', () => {
        const callback = vi.fn(() => true);
        detector.startListening(callback);

        dispatchKey('keydown', 'a');
        const repeatedKeydown = dispatchKey('keydown', 'a', { repeat: true });
        expect(callback).toHaveBeenCalledTimes(1);
        expect(repeatedKeydown.stopPropagation).not.toHaveBeenCalled();

        dispatchKey('keyup', 'a');
        dispatchKey('keydown', 'a');
        expect(callback).toHaveBeenCalledTimes(2);
    });

    it.each(['F12', 'F5'])('leaves %s unhandled', (key) => {
        const callback = vi.fn(() => false);
        detector.startListening(callback);

        const { event, stopPropagation } = dispatchKey('keydown', key);

        expect(callback).not.toHaveBeenCalled();
        expect(stopPropagation).not.toHaveBeenCalled();
        expect(event.defaultPrevented).toBe(false);
        expect(detector.getPressedKeys()).toEqual([]);
    });

    it('stops with cancel=true when Escape is pressed', () => {
        const callbackStop = vi.fn();
        const callbackContinue = vi.fn(() => true);
        detector.startListening(callbackContinue, callbackStop);
        dispatchKey('keydown', 'a');

        dispatchKey('keydown', 'Escape');
        dispatchKey('keydown', 'b');

        expect(callbackStop).toHaveBeenCalledExactlyOnceWith(true);
        expect(callbackContinue).toHaveBeenCalledTimes(1);
        expect(detector.getPressedKeys()).toEqual([]);
    });

    it('stops with cancel=false when Delete is pressed', () => {
        const callbackStop = vi.fn();
        detector.startListening(() => true, callbackStop);

        dispatchKey('keydown', 'Delete');
        dispatchKey('keydown', 'b');

        expect(callbackStop).toHaveBeenCalledExactlyOnceWith(false);
    });
});