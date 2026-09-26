import { beforeEach, describe, expect, it } from 'vitest';
import SharedSoundBoardUtil from '@/modules/SharedSoundBoardUtil';

describe('SharedSoundBoardUtil', () => {
    beforeEach(() => {
        document.body.innerHTML = '';
    });

    it('returns null when the active websocket element is missing', () => {
        expect(SharedSoundBoardUtil.getSlaveUrl()).toBeNull();
        expect(SharedSoundBoardUtil.isSlavePage()).toBe(false);
    });

    it('returns null when the active websocket element has no URL', () => {
        document.body.innerHTML = '<div id="active-WS"></div>';

        expect(SharedSoundBoardUtil.getSlaveUrl()).toBeNull();
        expect(SharedSoundBoardUtil.isSlavePage()).toBe(false);
    });

    it('returns the URL and identifies a slave page when configured', () => {
        document.body.innerHTML = '<div id="active-WS" data-url="wss://example.test/socket"></div>';

        expect(SharedSoundBoardUtil.getSlaveUrl()).toBe('wss://example.test/socket');
        expect(SharedSoundBoardUtil.isSlavePage()).toBe(true);
    });
});