import ConsoleCustom from '@/modules/General/ConsoleCustom';
import ScriptActionRegistry from '@/modules/Script/ScriptActionRegistry';
import ScriptScheduler from '@/modules/Script/ScriptScheduler';
import { ScriptStepHandle } from '@/modules/Script/IScriptAction';
import { ScriptDTO, ScriptStepDTO } from '@/modules/Script/ScriptTypes';

/**
 * Exécute un script : une instance correspond à une exécution.
 *
 * Le runner résout les déclencheurs (immédiat, timecode, fin d'une étape) et
 * délègue chaque action au ScriptActionRegistry.
 */
class ScriptRunner {
    private readonly scheduler = new ScriptScheduler();
    private readonly handles = new Map<string, ScriptStepHandle>();
    private readonly executedSteps = new Set<string>();
    private readonly dependents = new Map<string, ScriptStepDTO[]>();
    private pending = 0;
    private running = false;

    constructor(
        private readonly script: ScriptDTO,
        private readonly onFinished: () => void = () => { }
    ) { }

    isRunning(): boolean {
        return this.running;
    }

    start(): void {
        if (this.running) return;
        this.running = true;
        this.indexDependentSteps();

        this.retain();
        for (const step of this.script.steps) {
            if (step.trigger_type === 'IMMEDIATE') {
                this.scheduleStep(step, 0);
            } else if (step.trigger_type === 'TIMECODE') {
                this.scheduleStep(step, step.trigger_offset_ms);
            }
        }
        this.release();
    }

    stop(): void {
        if (!this.running) return;
        this.running = false;
        this.scheduler.dispose();
        for (const handle of this.handles.values()) {
            handle.stop();
        }
        this.handles.clear();
        this.onFinished();
    }

    private indexDependentSteps(): void {
        for (const step of this.script.steps) {
            if (step.trigger_type !== 'ON_STEP_END' || !step.trigger_source_step_uuid) continue;
            const siblings = this.dependents.get(step.trigger_source_step_uuid) ?? [];
            siblings.push(step);
            this.dependents.set(step.trigger_source_step_uuid, siblings);
        }
    }

    private scheduleStep(step: ScriptStepDTO, delayMs: number): void {
        this.retain();
        this.scheduler.scheduleAfter(delayMs, () => {
            this.runStep(step);
            this.release();
        });
    }

    private runStep(step: ScriptStepDTO): void {
        if (!this.running || this.executedSteps.has(step.uuid)) return;
        this.executedSteps.add(step.uuid);

        const action = ScriptActionRegistry.resolve(step.action_type);
        if (!action) {
            ConsoleCustom.error(`Unknown script action ${step.action_type}`);
            return;
        }

        let handle: ScriptStepHandle;
        try {
            handle = action.execute(step, { scriptUuid: this.script.uuid });
        } catch (error) {
            ConsoleCustom.error(`Script step ${step.uuid} failed`, error);
            return;
        }

        this.handles.set(step.uuid, handle);
        this.attachDependents(step, handle);
    }

    private attachDependents(step: ScriptStepDTO, handle: ScriptStepHandle): void {
        const dependents = this.dependents.get(step.uuid);
        if (!dependents?.length) return;

        this.retain();
        let settled = false;
        handle.onEnd(() => {
            if (settled) return;
            settled = true;
            for (const dependent of dependents) {
                this.scheduleStep(dependent, dependent.trigger_offset_ms);
            }
            this.release();
        });
    }

    private retain(): void {
        this.pending += 1;
    }

    private release(): void {
        this.pending -= 1;
        if (this.pending <= 0 && this.running) {
            this.finish();
        }
    }

    private finish(): void {
        this.running = false;
        this.scheduler.dispose();
        for (const handle of this.handles.values()) {
            handle.release();
        }
        this.handles.clear();
        this.onFinished();
    }
}

export default ScriptRunner;
