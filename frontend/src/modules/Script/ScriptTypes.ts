export type ScriptActionType = 'PLAY_PLAYLIST' | 'STOP_PLAYLIST' | 'SET_VOLUME' | 'PLAY_TRACK' | string;
export type ScriptTriggerType = 'IMMEDIATE' | 'TIMECODE' | 'ON_STEP_END' | string;

export interface ScriptStepDTO {
    uuid: string;
    order: number;
    action_type: ScriptActionType;
    trigger_type: ScriptTriggerType;
    trigger_offset_ms: number;
    trigger_source_step_uuid: string | null;
    params: Record<string, unknown>;
}

export interface ScriptDTO {
    uuid: string;
    name: string;
    color: string;
    colorText: string;
    order: number;
    enabled: boolean;
    steps: ScriptStepDTO[];
}
