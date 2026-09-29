import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { SearchMusicElement } from '@/modules/MusicElementSearcher';
import UpdateVolumeElement from '@/modules/UpdateVolumeElement';
import { UpdateVolumePlaylist } from '@/modules/UpdateVolumePlaylist';

const volumeMocks = vi.hoisted(() => ({
    searchMusic: vi.fn(),
    clearAllCache: vi.fn(),
    clearCache: vi.fn(),
    updateElement: vi.fn(),
    getCsrfToken: vi.fn(),
}));

vi.mock('@/modules/MusicElementSearcher', () => ({
    SearchMusicElement: { searchByButton: volumeMocks.searchMusic },
}));

vi.mock('@/modules/UpdateVolumeElement', () => ({
    default: class {
        clearCache(playlistId: string) {
            volumeMocks.clearCache(playlistId);
            return this;
        }

        update() {
            volumeMocks.updateElement();
        }

        static clearAllCache() {
            volumeMocks.clearAllCache();
        }
    },
}));

vi.mock('@/modules/General/Csrf', () => ({
    default: { getToken: volumeMocks.getCsrfToken },
}));

describe('UpdateVolumePlaylist', () => {
    beforeEach(() => {
        vi.clearAllMocks();
        volumeMocks.getCsrfToken.mockReturnValue('csrf-token');
    });

    afterEach(() => {
        vi.unstubAllGlobals();
    });

    it('updates matching music elements and clears their cached volume', () => {
        const musicElement = {
            idPlaylist: 'playlist-1',
            setDefaultVolume: vi.fn(),
        };
        const buttonPlaylist = {
            dataset: {} as DOMStringMap,
            getVolume: vi.fn().mockReturnValue(0.65),
        };
        volumeMocks.searchMusic.mockReturnValue([musicElement]);
        const updater = new UpdateVolumePlaylist(buttonPlaylist as never);

        updater.updateVolume(65);
        updater.clearCache();

        expect(buttonPlaylist.dataset.playlistVolume).toBe('65');
        expect(musicElement.setDefaultVolume).toHaveBeenCalledWith(0.65);
        expect(volumeMocks.clearCache).toHaveBeenCalledWith('playlist-1');
        expect(volumeMocks.updateElement).toHaveBeenCalledOnce();
        expect(volumeMocks.clearAllCache).toHaveBeenCalledOnce();
        expect(SearchMusicElement.searchByButton).toHaveBeenCalledWith(buttonPlaylist);
        expect(UpdateVolumeElement).toBeDefined();
    });

    it('posts the volume and CSRF token to the backend', () => {
        const fetchMock = vi.fn();
        vi.stubGlobal('fetch', fetchMock);

        new UpdateVolumePlaylist({} as never).updateBackend('/api/volume', 0.4);

        expect(fetchMock).toHaveBeenCalledWith('/api/volume', {
            method: 'POST',
            headers: {
                Accept: 'application/json',
                'Content-Type': 'application/json',
                'X-CSRFToken': 'csrf-token',
            },
            body: JSON.stringify({ volume: 0.4 }),
        });
    });
});