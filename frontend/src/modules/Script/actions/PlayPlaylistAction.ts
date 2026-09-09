import { ButtonPlaylistFinder } from '@/modules/ButtonPlaylist';
import { SoundBoardManager } from '@/modules/SoundBoardManager';
import { IScriptAction, ScriptStepHandle } from '@/modules/Script/IScriptAction';
import { InstantStepHandle, PlaylistStepHandle } from '@/modules/Script/ScriptStepHandles';
import { ScriptStepDTO } from '@/modules/Script/ScriptTypes';

class PlayPlaylistAction implements IScriptAction {
    execute(step: ScriptStepDTO): ScriptStepHandle {
        const playlistUuid = step.params.playlist_uuid;
        const playlistId = typeof playlistUuid === 'string' ? playlistUuid : '';
        const buttonPlaylist = ButtonPlaylistFinder.search(playlistId);
        if (!buttonPlaylist) {
            return new InstantStepHandle();
        }

        if (!buttonPlaylist.isActive()) {
            buttonPlaylist.active();
            SoundBoardManager.addPlaylist(buttonPlaylist);
        }

        return new PlaylistStepHandle(playlistId);
    }
}

export default PlayPlaylistAction;
