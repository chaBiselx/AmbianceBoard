import { beforeEach, describe, expect, it, vi } from 'vitest';
import { PlaylistBadgeHandler } from '@/modules/SoundboardOrganizer/PlaylistBadgeHandler';
import { PlaylistOrderNormalizer } from '@/modules/SoundboardOrganizer/PlaylistOrder';
import { SectionConfig } from '@/modules/SoundboardOrganizer/OrganizerDom';

vi.mock('@/modules/General/ConsoleTesteur', () => ({
    default: { info: vi.fn() },
}));

describe('PlaylistOrderNormalizer', () => {
    beforeEach(() => {
        document.body.innerHTML = '';
        SectionConfig.refreshMaxSections();
    });

    it('sets playlist order and section number from the DOM order in every section', () => {
        document.body.innerHTML = `
            <div id="associated-playlists-section-1">
                <div class="playlist-dragAndDrop" data-order="9" data-section="4"></div>
                <div class="playlist-dragAndDrop" data-order="8" data-section="4"></div>
            </div>
            <div id="associated-playlists-section-2">
                <div class="playlist-dragAndDrop" data-order="7" data-section="4"></div>
            </div>
        `;

        new PlaylistOrderNormalizer().normalizeAll();

        const firstSection = document.getElementById('associated-playlists-section-1')!;
        const secondSection = document.getElementById('associated-playlists-section-2')!;
        const firstSectionPlaylists = [...firstSection.getElementsByClassName('playlist-dragAndDrop')] as HTMLDivElement[];
        const secondSectionPlaylist = secondSection.getElementsByClassName('playlist-dragAndDrop')[0] as HTMLDivElement;
        expect(firstSectionPlaylists.map(playlist => [playlist.dataset.order, playlist.dataset.section])).toEqual([
            ['1', '1'],
            ['2', '1'],
        ]);
        expect([secondSectionPlaylist.dataset.order, secondSectionPlaylist.dataset.section]).toEqual(['1', '2']);
    });
});

describe('PlaylistBadgeHandler', () => {
    beforeEach(() => {
        document.body.innerHTML = '';
        SectionConfig.refreshMaxSections();
    });

    it('refreshes badges for identified associated playlists and leaves unidentified playlists untouched', () => {
        document.body.innerHTML = `
            <div id="associated-playlists-section-1">
                <div id="playlist-1" class="playlist-dragAndDrop" data-order="3">
                    <span class="badge-order">stale</span>
                </div>
                <div class="playlist-dragAndDrop" data-order="4">
                    <span class="badge-order">unidentified</span>
                </div>
                <div id="playlist-without-order" class="playlist-dragAndDrop">
                    <span class="badge-order">stale</span>
                </div>
            </div>
            <div id="unassociated-playlists"></div>
        `;

        new PlaylistBadgeHandler().refresh();

        const playlist = document.getElementById('playlist-1')!;
        expect(playlist.querySelectorAll('.badge-order')).toHaveLength(1);
        expect(playlist.querySelector('.badge-order')?.textContent).toBe('3');

        const unidentifiedPlaylist = document.querySelectorAll('.playlist-dragAndDrop')[1];
        expect(unidentifiedPlaylist.querySelector('.badge-order')?.textContent).toBe('unidentified');

        const playlistWithoutOrder = document.getElementById('playlist-without-order')!;
        expect(playlistWithoutOrder.querySelector('.badge-order')?.textContent).toBe('+');
    });

    it('clears badges and order data for identified unassociated playlists', () => {
        document.body.innerHTML = `
            <div id="associated-playlists-section-1"></div>
            <div id="unassociated-playlists">
                <div id="playlist-2" class="playlist-dragAndDrop" data-order="2">
                    <span class="badge-order">2</span>
                </div>
                <div class="playlist-dragAndDrop" data-order="3">
                    <span class="badge-order">unidentified</span>
                </div>
            </div>
        `;

        new PlaylistBadgeHandler().refresh();

        const playlist = document.getElementById('playlist-2')!;
        expect(playlist.dataset.order).toBe('');
        expect(playlist.querySelector('.badge-order')).toBeNull();

        const unidentifiedPlaylist = document.querySelector('#unassociated-playlists .playlist-dragAndDrop')!.nextElementSibling!;
        expect(unidentifiedPlaylist.querySelector('.badge-order')?.textContent).toBe('unidentified');
    });
});
