import { beforeEach, describe, expect, it, vi } from 'vitest';

const mocks = vi.hoisted(() => ({
    getSlaveUrl: vi.fn(),
    getSlaveInstance: vi.fn(),
    start: vi.fn(),
    sendMessage: vi.fn(),
}));

vi.mock('@/modules/SharedSoundBoardWebSocket.js', () => ({
    default: { getSlaveInstance: mocks.getSlaveInstance },
}));

vi.mock('@/modules/SharedSoundBoardUtil.js', () => ({
    default: { getSlaveUrl: mocks.getSlaveUrl },
}));

import SharedSoundboardSendCmdMaster from '@/modules/SharedSoundboardSendCmdMaster';

describe('SharedSoundboardSendCmdMaster', () => {
    beforeEach(() => {
        vi.clearAllMocks();
        mocks.getSlaveUrl.mockReturnValue(null);
        mocks.getSlaveInstance.mockReturnValue({ start: mocks.start, sendMessage: mocks.sendMessage });
    });

    it('does not create a websocket or send a command without a slave URL', () => {
        const sender = new SharedSoundboardSendCmdMaster();
        sender.sendPlayPlaylistOnMaster('playlist-1');

        expect(mocks.getSlaveInstance).not.toHaveBeenCalled();
        expect(mocks.start).not.toHaveBeenCalled();
        expect(mocks.sendMessage).not.toHaveBeenCalled();
    });

    it('starts the slave websocket and sends the playlist command', () => {
        mocks.getSlaveUrl.mockReturnValue('wss://example.test/socket');

        const sender = new SharedSoundboardSendCmdMaster();
        sender.sendPlayPlaylistOnMaster('playlist-1');

        expect(mocks.getSlaveInstance).toHaveBeenCalledWith('wss://example.test/socket');
        expect(mocks.start).toHaveBeenCalledOnce();
        expect(mocks.sendMessage).toHaveBeenCalledWith({
            type: 'player_play_on_master',
            data: { playlist_uuid: 'playlist-1' },
        });
    });
});