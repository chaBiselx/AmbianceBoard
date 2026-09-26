import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import SetVolumeAction from '@/modules/Script/actions/SetVolumeAction';
import { ScriptStepDTO } from '@/modules/Script/ScriptTypes';

const actionMocks = vi.hoisted(() => ({
    findPlaylist: vi.fn(),
    setPlaylistVolume: vi.fn(),
}));

vi.mock('@/modules/ButtonPlaylist', () => ({
    ButtonPlaylistFinder: { search: actionMocks.findPlaylist },
}));

vi.mock('@/modules/UpdateVolumePlaylist', () => ({
    UpdateVolumePlaylist: class {
        updateVolume(volume: number) {
            actionMocks.setPlaylistVolume(volume);
        }
    },
}));

describe('volume actions', () => {
    beforeEach(() => {
        vi.clearAllMocks();
    });

    it.each([
        { requested: -20, expected: 0 },
        { requested: 45, expected: 45 },
        { requested: 150, expected: 100 },
    ])('clamps script volume $requested to $expected', ({ requested, expected }) => {
        actionMocks.findPlaylist.mockReturnValue({});

        new SetVolumeAction().execute({
            params: { playlist_uuid: 'playlist-1', volume: requested },
        } as ScriptStepDTO);

        expect(actionMocks.findPlaylist).toHaveBeenCalledWith('playlist-1');
        expect(actionMocks.setPlaylistVolume).toHaveBeenCalledWith(expected);
    });

    it('ignores missing playlists and defaults an omitted volume to full volume', () => {
        actionMocks.findPlaylist.mockReturnValueOnce(null).mockReturnValueOnce({});
        const action = new SetVolumeAction();

        action.execute({ params: { playlist_uuid: 'missing' } } as ScriptStepDTO);
        action.execute({ params: { playlist_uuid: 'found' } } as ScriptStepDTO);

        expect(actionMocks.setPlaylistVolume).toHaveBeenCalledOnce();
        expect(actionMocks.setPlaylistVolume).toHaveBeenCalledWith(100);
    });

});