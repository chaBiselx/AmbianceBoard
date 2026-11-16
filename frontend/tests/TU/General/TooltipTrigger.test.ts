import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import * as bootstrap from 'bootstrap';
import ConsoleCustom from '@/modules/General/ConsoleCustom';
import TooltipTrigger from '@/modules/General/TooltipTrigger';

vi.mock('bootstrap', () => ({
    Tooltip: {
        getOrCreateInstance: vi.fn(),
    },
}));

vi.mock('@/modules/General/ConsoleCustom', () => ({
    default: { warn: vi.fn() },
}));

describe('TooltipTrigger', () => {
    beforeEach(() => {
        document.body.innerHTML = '';
        vi.mocked(bootstrap.Tooltip.getOrCreateInstance).mockReset();
        vi.mocked(ConsoleCustom.warn).mockReset();
    });

    afterEach(() => {
        vi.useRealTimers();
        vi.restoreAllMocks();
    });

    it('shows the targeted tooltip and auto-hides it five seconds after the last click', () => {
        vi.useFakeTimers();
        document.body.innerHTML = `
            <button class="js-tooltip-trigger" data-tooltip-target="target-tooltip">
                Show information
            </button>
            <span id="target-tooltip" data-bs-toggle="tooltip"></span>
        `;
        const tooltipTarget = document.getElementById('target-tooltip')!;
        const show = vi.fn();
        const hide = vi.fn();
        vi.mocked(bootstrap.Tooltip.getOrCreateInstance).mockReturnValue({ show, hide } as any);

        new TooltipTrigger().addEventListener();
        const trigger = document.querySelector('.js-tooltip-trigger')!;
        trigger.dispatchEvent(new Event('click', { bubbles: true }));

        expect(bootstrap.Tooltip.getOrCreateInstance).toHaveBeenCalledWith(tooltipTarget);
        expect(show).toHaveBeenCalledOnce();
        vi.advanceTimersByTime(4000);
        trigger.dispatchEvent(new Event('click', { bubbles: true }));
        expect(show).toHaveBeenCalledTimes(2);
        vi.advanceTimersByTime(1000);
        expect(hide).not.toHaveBeenCalled();
        vi.advanceTimersByTime(4000);
        expect(hide).toHaveBeenCalledOnce();
    });

    it('warns when a trigger references a missing target', () => {
        document.body.innerHTML = `
            <button class="js-tooltip-trigger" data-tooltip-target="missing-tooltip"></button>
        `;

        new TooltipTrigger().addEventListener();
        document.querySelector('.js-tooltip-trigger')?.dispatchEvent(new Event('click', { bubbles: true }));

        expect(ConsoleCustom.warn).toHaveBeenCalledWith('Tooltip trigger target not found: missing-tooltip');
    });
});
