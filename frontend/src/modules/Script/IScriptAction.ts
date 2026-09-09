import { ScriptStepDTO } from '@/modules/Script/ScriptTypes';

/**
 * Poignée retournée par une action de script.
 *
 * `release()` ne coupe que les abonnements, `stop()` annule en plus les effets
 * produits par l'action.
 */
export interface ScriptStepHandle {
    onEnd(callback: () => void): void;
    release(): void;
    stop(): void;
}

export interface ScriptActionContext {
    scriptUuid: string;
}

export interface IScriptAction {
    execute(step: ScriptStepDTO, context: ScriptActionContext): ScriptStepHandle;
}
