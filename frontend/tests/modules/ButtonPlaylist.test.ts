import { describe, it, expect, beforeEach, vi } from 'vitest';
import { ButtonPlaylist, ButtonPlaylistFinder, ListingButtonPlaylist } from '@/modules/ButtonPlaylist';
import Boolean from '@/modules/Util/Boolean';

// Mock de la classe Boolean pour isoler les tests de ButtonPlaylist
vi.mock('@/modules/Util/Boolean', () => ({
    default: {
        convert: vi.fn((value) => {
            if (typeof value === 'boolean') return value;
            return value === 'true';
        })
    }
}));

describe('ButtonPlaylist.ts', () => {

    describe('ButtonPlaylist', () => {
        let buttonElement: HTMLElement;
        let buttonPlaylist: ButtonPlaylist;

        beforeEach(() => {
            document.body.innerHTML = `
                <div 
                    id="playlist-123"
                    data-playlist-id="123"
                    data-playlist-singleconcurrentread="true"
                    data-playlist-type="music"
                    data-playlist-volume="50"
                ></div>
            `;
            buttonElement = document.getElementById('playlist-123')!;
            buttonPlaylist = new ButtonPlaylist(buttonElement);
        });

        it('should initialize properties correctly from dataset', () => {
            expect(buttonPlaylist.idPlaylist).toBe('123');
            expect(buttonPlaylist.singleConcurrentread).toBe(true);
            expect(buttonPlaylist.playlistType).toBe('music');
            expect(buttonPlaylist.dataset).toBe(buttonElement.dataset);
            expect(Boolean.convert).toHaveBeenCalledWith('true');
        });

        it('should return the correct volume', () => {
            expect(buttonPlaylist.getVolume()).toBe(0.5);
        });

        it('should return default volume of 1 if not specified', () => {
            delete buttonElement.dataset.playlistVolume;
            const newButtonPlaylist = new ButtonPlaylist(buttonElement);
            expect(newButtonPlaylist.getVolume()).toBe(1);
        });

        it('should delete the element from the DOM', () => {
            const removeSpy = vi.spyOn(buttonElement, 'remove');
            buttonPlaylist.delete();
            expect(removeSpy).toHaveBeenCalledTimes(1);
        });

        it('should activate the playlist button', () => {
            buttonPlaylist.active();
            expect(buttonPlaylist.isActive()).toBe(true);
            expect(buttonElement.classList.contains('active-playlist')).toBe(true);
            expect(buttonPlaylist.getToken()).not.toBeNull();
        });

        it('should deactivate the playlist button', () => {
            buttonPlaylist.active(); // d'abord l'activer
            buttonPlaylist.disactive();
            expect(buttonPlaylist.isActive()).toBe(false);
            expect(buttonElement.classList.contains('active-playlist')).toBe(false);
            expect(buttonPlaylist.getToken()).toBeNull();
        });

        it('should return the correct playlist ID', () => {
            expect(buttonPlaylist.getIdPlaylist()).toBe('123');
        });
    });

    describe('ButtonPlaylistFinder', () => {
        beforeEach(() => {
            document.body.innerHTML = `
                <div id="playlist-456" data-playlist-id="456"></div>
            `;
        });

        it('should find and return a ButtonPlaylist instance if element exists', () => {
            const found = ButtonPlaylistFinder.search('456');
            expect(found).toBeInstanceOf(ButtonPlaylist);
            expect(found?.getIdPlaylist()).toBe('456');
        });

        it('should return null if element does not exist', () => {
            const notFound = ButtonPlaylistFinder.search('999');
            expect(notFound).toBeNull();
        });
    });

    describe('ListingButtonPlaylist', () => {
        beforeEach(() => {
            document.body.innerHTML = `
                <div class="playlist-music" data-playlist-id="1"></div>
                <div class="playlist-ambient" data-playlist-id="2"></div>
                <div class="playlist-music" data-playlist-id="3"></div>
            `;
        });

        it('should return a list of ButtonPlaylist instances for a given type', () => {
            const musicPlaylists = ListingButtonPlaylist.getListingAudioElement('music');
            expect(musicPlaylists).toHaveLength(2);
            expect(musicPlaylists[0]).toBeInstanceOf(ButtonPlaylist);
            expect(musicPlaylists[1].getIdPlaylist()).toBe('3');
        });

        it('should return an empty list if no elements of the type are found', () => {
            const sfxPlaylists = ListingButtonPlaylist.getListingAudioElement('sfx');
            expect(sfxPlaylists).toHaveLength(0);
        });
    });
});
