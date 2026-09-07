import { ButtonPlaylistFinder } from '@/modules/ButtonPlaylist';
import { UpdateVolumePlaylist } from '@/modules/UpdateVolumePlaylist';
import { IScriptAction, ScriptStepHandle } from '@/modules/Script/IScriptAction';
import { InstantStepHandle } from '@/modules/Script/ScriptStepHandles';
import { ScriptStepDTO } from '@/modules/Script/ScriptTypes';

class SetVolumeAction implements IScriptAction {
    execute(step: ScriptStepDTO): ScriptStepHandle {
        const playlistUuid = step.params.playlist_uuid;
        const playlistId = typeof playlistUuid === 'string' ? playlistUuid : '';
        const buttonPlaylist = ButtonPlaylistFinder.search(playlistId);
        if (buttonPlaylist) {
            const volume = Number(step.params.volume ?? 100);
            new UpdateVolumePlaylist(buttonPlaylist).updateVolume(Math.min(100, Math.max(0, volume)));
        }
        return new InstantStepHandle();
    }
}

export default SetVolumeAction;
