import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import ShowConsoleBetaTester from '../../../src/modules/General/ShowConsoleBetaTester';
import ConsoleTraceServeur from '../../../src/modules/General/ConsoleTraceServeur';

vi.mock('@/modules/General/ConsoleTraceServeur', () => ({
    default: { log: vi.fn() },
}));

describe('ShowConsoleBetaTester', () => {
    beforeEach(() => {
        document.body.innerHTML = '<button id="showLoggerBetaTest"></button><div id="betaTestConsole" class="d-none"></div>';
        vi.clearAllMocks();
    });

    afterEach(() => {
        vi.restoreAllMocks();
    });

    it('toggles the console and logs when it becomes visible', () => {
        new ShowConsoleBetaTester().addEvent();
        const button = document.getElementById('showLoggerBetaTest')!;
        const consoleElement = document.getElementById('betaTestConsole')!;

        button.click();
        expect(consoleElement.classList.contains('d-none')).toBe(false);
        expect(ConsoleTraceServeur.log).toHaveBeenCalledWith('Set console beta tester visible');

        button.click();
        expect(consoleElement.classList.contains('d-none')).toBe(true);
        expect(ConsoleTraceServeur.log).toHaveBeenCalledTimes(1);
    });
});
