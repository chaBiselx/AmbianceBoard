import { beforeEach, describe, expect, it, vi } from 'vitest';
import { SoundBoardManager } from '@/modules/SoundBoardManager';
import type { ButtonPlaylist } from '@/modules/ButtonPlaylist';
import { ListingButtonPlaylist } from '@/modules/ButtonPlaylist';
import { ListingAudioElement } from '@/modules/MusicElementSearcher';
import { MusicElementFactory } from '@/modules/MusicElementFactory';

const managerMocks = vi.hoisted(() => ({
    listingPlaylists: vi.fn(),
    listingAudio: vi.fn(),
    allAudio: vi.fn(),
    fromButton: vi.fn(),
    fromAudio: vi.fn(),
    updateVolume: vi.fn(),
    log: vi.fn(),
}));

vi.mock('@/modules/ButtonPlaylist', () => ({
    ListingButtonPlaylist: { getListingAudioElement: managerMocks.listingPlaylists },
}));

vi.mock('@/modules/MusicElementSearcher', () => ({
    ListingAudioElement: {
        getListingAudioElement: managerMocks.listingAudio,
        getListAllAudio: managerMocks.allAudio,
    },
}));

vi.mock('@/modules/MusicElementFactory', () => ({
    MusicElementFactory: {
        fromButtonPlaylist: managerMocks.fromButton,
        fromAudioElement: managerMocks.fromAudio,
    },
}));

vi.mock('@/modules/UpdateVolumeElement', () => ({
    default: class {
        update() {
            managerMocks.updateVolume();
        }
    },
}));

vi.mock('@/modules/General/ConsoleTesteur', () => ({ default: { log: managerMocks.log } }));
vi.mock('@/modules/General/ConsoleCustom', () => ({ default: { log: managerMocks.log } }));

describe('SoundBoardManager', () => {
    beforeEach(() => {
        vi.clearAllMocks();
        document.body.innerHTML = '';
    });

    it('creates and starts a playlist when no matching audio is playing', () => {
        const musicElement = { addToDOM: vi.fn(), play: vi.fn() };
        const button = { idPlaylist: 'one', singleConcurrentread: false } as ButtonPlaylist;
        managerMocks.fromButton.mockReturnValue(musicElement);

        SoundBoardManager.addPlaylist(button);

        expect(managerMocks.fromButton).toHaveBeenCalledWith(button);
        expect(managerMocks.updateVolume).toHaveBeenCalledOnce();
        expect(musicElement.addToDOM).toHaveBeenCalledOnce();
        expect(musicElement.play).toHaveBeenCalledOnce();
    });

    it('removes all matching audio and deactivates the playlist when it is already playing', () => {
        document.body.innerHTML = '<audio class="playlist-audio-one"></audio><audio class="playlist-audio-one"></audio>';
        const musicElements = [{ delete: vi.fn() }, { delete: vi.fn() }];
        managerMocks.fromAudio.mockImplementation((element: Element) => musicElements[Array.from(document.querySelectorAll('audio')).indexOf(element)]);
        const button = {
            idPlaylist: 'one',
            disactive: vi.fn(),
            singleConcurrentread: false,
        } as unknown as ButtonPlaylist;

        SoundBoardManager.addPlaylist(button);

        expect(button.disactive).toHaveBeenCalledOnce();
        expect(musicElements.map(element => element.delete)).toEqual([
            expect.any(Function), expect.any(Function),
        ]);
        expect(musicElements[0].delete).toHaveBeenCalledOnce();
        expect(musicElements[1].delete).toHaveBeenCalledOnce();
    });

    it('deletes same-type playlists and deactivates their buttons for concurrent playlists', () => {
        const musicElement = { delete: vi.fn() };
        const otherButton = { disactive: vi.fn() };
        managerMocks.listingAudio.mockReturnValue([musicElement]);
        managerMocks.listingPlaylists.mockReturnValue([otherButton]);

        SoundBoardManager.deleteSameTypePlaylist({
            singleConcurrentread: true,
            playlistType: 'music',
        } as ButtonPlaylist);

        expect(ListingAudioElement.getListingAudioElement).toHaveBeenCalledWith('music');
        expect(ListingButtonPlaylist.getListingAudioElement).toHaveBeenCalledWith('music');
        expect(musicElement.delete).toHaveBeenCalledOnce();
        expect(otherButton.disactive).toHaveBeenCalledOnce();
    });

    it('removes every audio element when all playlists are cleared', () => {
        const musicElement = { delete: vi.fn() };
        managerMocks.allAudio.mockReturnValue([musicElement]);

        SoundBoardManager.deleteAllMusicPlaylist();

        expect(musicElement.delete).toHaveBeenCalledOnce();
    });
});