import ConsoleCustom from '@/modules/General/ConsoleCustom';
import ScriptCooldownGuard from '@/modules/Script/ScriptCooldownGuard';
import ScriptRunner from '@/modules/Script/ScriptRunner';
import { ScriptDTO } from '@/modules/Script/ScriptTypes';

const ACTIVE_CLASS = 'active-script';

/**
 * Câble le panneau de scripts du soundboard : lecture du JSON injecté par le
 * backend, gestion du cooldown et du cycle de vie des runners.
 */
class ScriptManager {
    private readonly scripts = new Map<string, ScriptDTO>();
    private readonly runners = new Map<string, ScriptRunner>();
    private guard: ScriptCooldownGuard = new ScriptCooldownGuard(0);

    init(): void {
        const container = document.getElementById('script-list');
        if (!container) return;

        this.guard = new ScriptCooldownGuard(Number.parseInt(container.dataset.scriptCooldown ?? '0', 10) || 0);
        this.loadScripts();

        for (const element of container.querySelectorAll<HTMLButtonElement>('.script-link')) {
            element.addEventListener('click', () => this.toggleScript(element));
        }
    }

    private loadScripts(): void {
        const dataElement = document.getElementById('scripts-data');
        if (!dataElement?.textContent) return;
        try {
            const parsed = JSON.parse(dataElement.textContent) as ScriptDTO[];
            for (const script of parsed) {
                this.scripts.set(script.uuid, script);
            }
        } catch (error) {
            ConsoleCustom.error('Unable to parse scripts payload', error);
        }
    }

    private toggleScript(button: HTMLButtonElement): void {
        const scriptUuid = button.dataset.scriptUuid;
        if (!scriptUuid) return;

        const runner = this.runners.get(scriptUuid);
        if (runner?.isRunning()) {
            runner.stop();
            return;
        }


        if (!this.guard.canStart(scriptUuid)) return;

        const script = this.scripts.get(scriptUuid);
        if (!script) return;

        this.guard.markStart(scriptUuid, button);
        button.classList.add(ACTIVE_CLASS);


        const newRunner = new ScriptRunner(script, () => {
            button.classList.remove(ACTIVE_CLASS);
            this.runners.delete(scriptUuid);
        });
        this.runners.set(scriptUuid, newRunner);
        newRunner.start();
    }
}

export default ScriptManager;
