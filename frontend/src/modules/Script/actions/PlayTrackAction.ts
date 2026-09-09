import { IScriptAction, ScriptStepHandle } from '@/modules/Script/IScriptAction';

/**
 * Placeholder : l'action est modélisée et validée côté backend mais n'est pas
 * encore exécutable. Elle sert de point d'extension pour la lecture d'une piste précise.
 */
class PlayTrackAction implements IScriptAction {
    execute(): ScriptStepHandle {
        throw new Error('PLAY_TRACK action is not implemented yet');
    }
}

export default PlayTrackAction;
