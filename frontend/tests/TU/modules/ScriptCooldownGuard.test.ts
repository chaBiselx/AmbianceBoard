import { beforeEach, describe, expect, it, vi } from 'vitest';
import ScriptCooldownGuard from '@/modules/Script/ScriptCooldownGuard';

describe('ScriptCooldownGuard', () => {
    beforeEach(() => {
        vi.useFakeTimers();
        vi.setSystemTime(new Date('2026-01-01T00:00:00Z'));
    });

    it('allows the first start', () => {
        expect(new ScriptCooldownGuard(2000).canStart('script-1')).toBe(true);
    });

    it('blocks a restart inside the cooldown window', () => {
        const guard = new ScriptCooldownGuard(2000);
        guard.markStart('script-1');

        vi.advanceTimersByTime(1999);
        expect(guard.canStart('script-1')).toBe(false);
    });

    it('allows a restart once the cooldown expired', () => {
        const guard = new ScriptCooldownGuard(2000);
        guard.markStart('script-1');

        vi.advanceTimersByTime(2000);
        expect(guard.canStart('script-1')).toBe(true);
    });

    it('tracks each script independently', () => {
        const guard = new ScriptCooldownGuard(2000);
        guard.markStart('script-1');

        expect(guard.canStart('script-2')).toBe(true);
    });

    it('disables the button during the cooldown then restores it', () => {
        const button = document.createElement('button');
        const guard = new ScriptCooldownGuard(2000);

        guard.markStart('script-1', button);
        expect(button.disabled).toBe(true);
        expect(button.classList.contains('script-cooldown')).toBe(true);

        vi.advanceTimersByTime(2000);
        expect(button.disabled).toBe(false);
        expect(button.classList.contains('script-cooldown')).toBe(false);
    });

    it('never blocks when the cooldown is disabled', () => {
        const guard = new ScriptCooldownGuard(0);
        guard.markStart('script-1');

        expect(guard.canStart('script-1')).toBe(true);
    });
});
