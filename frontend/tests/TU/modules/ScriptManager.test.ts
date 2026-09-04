import { beforeEach, describe, expect, it, vi } from 'vitest';

const runnerState = vi.hoisted(() => ({
    start: vi.fn(),
    stop: vi.fn(),
    running: false,
}));

vi.mock('@/modules/Script/ScriptRunner', () => ({
    default: class {
        constructor(_script: unknown, private readonly onFinished: () => void) { }

        start() {
            runnerState.running = true;
            runnerState.start();
        }

        stop() {
            runnerState.running = false;
            runnerState.stop();
            this.onFinished();
        }

        isRunning() {
            return runnerState.running;
        }
    }
}));

import ScriptManager from '@/modules/Script/ScriptManager';

const SCRIPT_UUID = 'script-1';

const setupDOM = (cooldownMs: number) => {
    document.body.innerHTML = `
        <div id="script-list" data-script-cooldown="${cooldownMs}">
            <button class="script-link" data-script-uuid="${SCRIPT_UUID}">Intro</button>
        </div>
        <script type="application/json" id="scripts-data">[{"uuid":"${SCRIPT_UUID}","name":"Intro","color":"#000","colorText":"#fff","order":0,"enabled":true,"steps":[]}]</script>
    `;
    return document.querySelector('.script-link') as HTMLButtonElement;
};

describe('ScriptManager', () => {
    beforeEach(() => {
        vi.clearAllMocks();
        vi.useFakeTimers();
        runnerState.running = false;
    });

    it('starts the script on click', () => {
        const button = setupDOM(2000);
        new ScriptManager().init();

        button.click();

        expect(runnerState.start).toHaveBeenCalledTimes(1);
        expect(button.classList.contains('active-script')).toBe(true);
    });

    it('ignores a second click inside the cooldown window', () => {
        const button = setupDOM(2000);
        new ScriptManager().init();

        button.click();
        runnerState.running = false;
        button.click();

        expect(runnerState.start).toHaveBeenCalledTimes(1);
    });

    it('stops a running script when clicked again', () => {
        const button = setupDOM(0);
        new ScriptManager().init();

        button.click();
        button.click();

        expect(runnerState.stop).toHaveBeenCalledTimes(1);
        expect(button.classList.contains('active-script')).toBe(false);
    });

    it('does nothing when the panel is absent', () => {
        document.body.innerHTML = '';
        expect(() => new ScriptManager().init()).not.toThrow();
    });
});
