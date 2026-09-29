import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import SoundBoardEventListener from '@/modules/SoundBoardEventListener';

const listenerMocks = vi.hoisted(() => ({
    addPlaylist: vi.fn(),
    removePlaylist: vi.fn(),
    sendPlay: vi.fn(),
}));

vi.mock('@/modules/SoundBoardManager', () => ({
    SoundBoardManager: {
        addPlaylist: listenerMocks.addPlaylist,
        removePlaylist: listenerMocks.removePlaylist,
    },
}));

vi.mock('@/modules/SharedSoundboardSendCmdMaster', () => ({
    default: class {
        sendPlayPlaylistOnMaster(playlistId: string) {
            listenerMocks.sendPlay(playlistId);
        }
    },
}));

describe('SoundBoardEventListener', () => {
    beforeEach(() => {
        vi.clearAllMocks();
        vi.useFakeTimers();
        document.body.innerHTML = `
            <button id="playlist-one" class="playlist-link" data-playlist-id="one" data-playlist-type="music" data-playlist-singleconcurrentread="false"></button>
            <button id="playlist-two" class="playlist-link playlist-user-playable" data-playlist-id="two" data-playlist-type="music" data-playlist-singleconcurrentread="false"></button>
            <button class="playlist-link disabled" data-playlist-id="disabled" data-playlist-type="music" data-playlist-singleconcurrentread="false"></button>
        `;
    });

    afterEach(() => {
        vi.useRealTimers();
    });

    it('toggles regular playlists on and off', () => {
        new SoundBoardEventListener().addEventListenerDom();
        const button = document.getElementById('playlist-one')!;

        button.click();
        expect(listenerMocks.addPlaylist).toHaveBeenCalledOnce();
        expect(button.classList.contains('active-playlist')).toBe(true);

        button.click();
        expect(listenerMocks.removePlaylist).toHaveBeenCalledOnce();
        expect(button.classList.contains('active-playlist')).toBe(false);
    });

    it('sends user-playable playlists to the master and deactivates them after one second', () => {
        new SoundBoardEventListener().addEventListenerDom();
        const button = document.getElementById('playlist-two')!;

        button.click();

        expect(listenerMocks.sendPlay).toHaveBeenCalledWith('two');
        expect(button.classList.contains('active-playlist')).toBe(true);
        vi.advanceTimersByTime(1000);
        expect(button.classList.contains('active-playlist')).toBe(false);
    });

    it('does not attach actions to disabled playlists', () => {
        new SoundBoardEventListener().addEventListenerDom();
        document.querySelector<HTMLButtonElement>('.disabled')!.click();

        expect(listenerMocks.addPlaylist).not.toHaveBeenCalled();
        expect(listenerMocks.removePlaylist).not.toHaveBeenCalled();
    });
});