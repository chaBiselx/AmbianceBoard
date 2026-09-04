import { IScriptAction } from '@/modules/Script/IScriptAction';
import PlayPlaylistAction from '@/modules/Script/actions/PlayPlaylistAction';
import PlayTrackAction from '@/modules/Script/actions/PlayTrackAction';
import SetVolumeAction from '@/modules/Script/actions/SetVolumeAction';
import StopPlaylistAction from '@/modules/Script/actions/StopPlaylistAction';
import { ScriptActionType } from '@/modules/Script/ScriptTypes';

/**
 * Point d'extension du moteur : associe un type d'action à son exécuteur.
 * Ajouter une action revient à l'enregistrer ici et à déclarer sa spécification
 * de paramètres côté backend.
 */
class ScriptActionRegistry {
    private static readonly actions = new Map<ScriptActionType, IScriptAction>();

    static register(actionType: ScriptActionType, action: IScriptAction): void {
        ScriptActionRegistry.actions.set(actionType, action);
    }

    static resolve(actionType: ScriptActionType): IScriptAction | null {
        return ScriptActionRegistry.actions.get(actionType) ?? null;
    }
}

ScriptActionRegistry.register('PLAY_PLAYLIST', new PlayPlaylistAction());
ScriptActionRegistry.register('STOP_PLAYLIST', new StopPlaylistAction());
ScriptActionRegistry.register('SET_VOLUME', new SetVolumeAction());
ScriptActionRegistry.register('PLAY_TRACK', new PlayTrackAction());

export default ScriptActionRegistry;
