import { ButtonPlaylistFinder } from '@/modules/ButtonPlaylist';
import { SoundBoardManager } from '@/modules/SoundBoardManager';
import { IScriptAction, ScriptStepHandle } from '@/modules/Script/IScriptAction';
import { InstantStepHandle } from '@/modules/Script/ScriptStepHandles';
import { ScriptStepDTO } from '@/modules/Script/ScriptTypes';

class StopPlaylistAction implements IScriptAction {
    execute(step: ScriptStepDTO): ScriptStepHandle {
        const playlistId = String(step.params.playlist_uuid ?? '');
        const buttonPlaylist = ButtonPlaylistFinder.search(playlistId);
        if (buttonPlaylist) {
            buttonPlaylist.disactive();
            SoundBoardManager.removePlaylist(buttonPlaylist);
        }
        return new InstantStepHandle();
    }
}

export default StopPlaylistAction;
