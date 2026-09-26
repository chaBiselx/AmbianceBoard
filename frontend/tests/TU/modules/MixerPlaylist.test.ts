import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { MixerPlaylist } from '@/modules/MixerPlaylist';

const mixerMocks = vi.hoisted(() => ({
    isSlavePage: vi.fn(),
    getMasterInstance: vi.fn(),
    sendMessage: vi.fn(),
    findPlaylist: vi.fn(),
    updateVolume: vi.fn(),
    updateBackend: vi.fn(),
    deleteSameTypePlaylist: vi.fn(),
    fromButtonPlaylist: vi.fn(),
    updateElement: vi.fn(),
    log: vi.fn(),
}));

vi.mock('@/modules/SharedSoundBoardUtil', () => ({
    default: { isSlavePage: mixerMocks.isSlavePage },
}));

vi.mock('@/modules/SharedSoundBoardWebSocket', () => ({
    default: { getMasterInstance: mixerMocks.getMasterInstance },
}));

vi.mock('@/modules/ButtonPlaylist', () => ({
    ButtonPlaylistFinder: { search: mixerMocks.findPlaylist },
}));

vi.mock('@/modules/UpdateVolumePlaylist', () => ({
    UpdateVolumePlaylist: class {
        updateVolume(volume: number) {
            mixerMocks.updateVolume(volume);
        }

        updateBackend(uri: string, volume: number) {
            mixerMocks.updateBackend(uri, volume);
        }
    },
}));

vi.mock('@/modules/SoundBoardManager', () => ({
    SoundBoardManager: { deleteSameTypePlaylist: mixerMocks.deleteSameTypePlaylist },
}));

vi.mock('@/modules/MusicElementFactory', () => ({
    MusicElementFactory: { fromButtonPlaylist: mixerMocks.fromButtonPlaylist },
}));

vi.mock('@/modules/UpdateVolumeElement', () => ({
    default: class {
        update() {
            mixerMocks.updateElement();
        }
    },
}));

vi.mock('@/modules/General/ConsoleCustom', () => ({ default: { log: mixerMocks.log } }));

describe('MixerPlaylist', () => {
    beforeEach(() => {
        vi.clearAllMocks();
        mixerMocks.isSlavePage.mockReturnValue(false);
        mixerMocks.getMasterInstance.mockReturnValue({ sendMessage: mixerMocks.sendMessage });
        document.body.innerHTML = '';
    });

    afterEach(() => {
        vi.unstubAllGlobals();
    });

    it('updates local volume, backend state, and the shared soundboard', () => {
        document.body.innerHTML = `
            <input id="saveVolumePlaylistMixer" type="checkbox" checked>
            <input class="mixer-playlist-update" data-idplaylist="playlist-1"
                data-playlistupdatevolumeuri="/api/volume" value="0.75">
        `;
        const buttonPlaylist = { getIdPlaylist: vi.fn().mockReturnValue('playlist-1') };
        mixerMocks.findPlaylist.mockReturnValue(buttonPlaylist);

        new MixerPlaylist().addEventListener();
        document.querySelector<HTMLInputElement>('.mixer-playlist-update')!
            .dispatchEvent(new Event('change', { bubbles: true }));

        expect(mixerMocks.findPlaylist).toHaveBeenCalledWith('playlist-1');
        expect(mixerMocks.updateVolume).toHaveBeenCalledWith(0.75);
        expect(mixerMocks.updateBackend).toHaveBeenCalledWith('/api/volume', 0.75);
        expect(mixerMocks.sendMessage).toHaveBeenCalledWith({
            type: 'send_playlist_update_volume',
            data: { playlist_uuid: 'playlist-1', volume: 0.75 },
        });
    });

    it('hides mixer controls and clears the save-backend selection when disabled', () => {
        document.body.innerHTML = `
            <input id="inputShowMixerPlaylist" type="checkbox">
            <input id="saveVolumePlaylistMixer" type="checkbox" checked>
            <span id="inputShowMixerPlaylist-show"></span>
            <span id="inputShowMixerPlaylist-hide" class="d-none"></span>
            <div id="saveVolumePlaylistMixer-div"></div>
            <div class="mixer-playlist-update-container"></div>
        `;
        new MixerPlaylist().addEventListener();

        document.getElementById('inputShowMixerPlaylist')!.dispatchEvent(new Event('change'));

        expect(document.querySelector('.mixer-playlist-update-container')!.classList.contains('hide-playlist-mixer')).toBe(true);
        expect((document.getElementById('saveVolumePlaylistMixer') as HTMLInputElement).checked).toBe(false);
        expect(document.getElementById('inputShowMixerPlaylist-show')!.classList.contains('d-none')).toBe(true);
    });

    it('loads specific tracks, plays a selected track, and closes the list', async () => {
        document.body.innerHTML = `
            <div class="responsive-sections-container" data-soundboard-tracks-uri="/api/tracks"></div>
            <input id="inputShowSpecificMusic" type="checkbox" checked>
            <span id="inputShowSpecificMusic-show"></span>
            <span id="inputShowSpecificMusic-hide" class="d-none"></span>
            <div class="js-specific-music d-none" data-playlist-id="playlist-1">
                <div class="specific-music-list"></div>
            </div>
            <div class="js-margin-specific-music d-none"></div>
        `;
        vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
            ok: true,
            json: async () => ({
                'playlist-1': [{ id: 4, name: 'Night Drive', duration: 95, uri: '/track/4' }],
            }),
        }));
        const buttonPlaylist = { active: vi.fn() };
        const musicElement = {
            setSpecificMusic: vi.fn(),
            addToDOM: vi.fn(),
            play: vi.fn(),
        };
        mixerMocks.findPlaylist.mockReturnValue(buttonPlaylist);
        mixerMocks.fromButtonPlaylist.mockReturnValue(musicElement);
        new MixerPlaylist().addEventListener();

        document.getElementById('inputShowSpecificMusic')!.dispatchEvent(new Event('change'));

        await vi.waitFor(() => expect(document.querySelector('.specific-music-item')).not.toBeNull());
        const track = document.querySelector<HTMLElement>('.specific-music-item')!;
        expect(track.dataset.trackId).toBe('4');
        expect(track.dataset.uri).toBe('/track/4');
        expect(track.textContent).toContain('Night Drive');
        track.click();

        expect(mixerMocks.deleteSameTypePlaylist).toHaveBeenCalledWith(buttonPlaylist);
        expect(musicElement.setSpecificMusic).toHaveBeenCalledWith('/track/4');
        expect(mixerMocks.updateElement).toHaveBeenCalledOnce();
        expect(musicElement.addToDOM).toHaveBeenCalledOnce();
        expect(musicElement.play).toHaveBeenCalledOnce();
        expect(buttonPlaylist.active).toHaveBeenCalledOnce();
        expect((document.getElementById('inputShowSpecificMusic') as HTMLInputElement).checked).toBe(false);
    });

    it('shows an empty state for a playlist without tracks', async () => {
        document.body.innerHTML = `
            <div class="responsive-sections-container" data-soundboard-tracks-uri="/api/tracks"></div>
            <input id="inputShowSpecificMusic" type="checkbox" checked>
            <div class="js-specific-music" data-playlist-id="empty"><div class="specific-music-list"></div></div>
        `;
        vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: true, json: async () => ({}) }));
        new MixerPlaylist().addEventListener();

        document.getElementById('inputShowSpecificMusic')!.dispatchEvent(new Event('change'));

        await vi.waitFor(() => expect(document.querySelector('.specific-music-empty')).not.toBeNull());
        expect(document.querySelector('.specific-music-empty')!.textContent).toContain('Aucune piste');
    });

    it('does not fetch tracks when the response is unsuccessful', async () => {
        document.body.innerHTML = `
            <div class="responsive-sections-container" data-soundboard-tracks-uri="/api/tracks"></div>
            <input id="inputShowSpecificMusic" type="checkbox" checked>
            <div class="js-specific-music" data-playlist-id="playlist-1"><div class="specific-music-list"></div></div>
        `;
        const fetchMock = vi.fn().mockResolvedValue({ ok: false });
        vi.stubGlobal('fetch', fetchMock);
        new MixerPlaylist().addEventListener();

        document.getElementById('inputShowSpecificMusic')!.dispatchEvent(new Event('change'));

        await vi.waitFor(() => expect(fetchMock).toHaveBeenCalledWith('/api/tracks'));
        expect(document.querySelector('.specific-music-item')).toBeNull();
    });
});