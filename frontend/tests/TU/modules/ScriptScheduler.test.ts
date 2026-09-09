import { beforeEach, describe, expect, it, vi } from 'vitest';
import ScriptScheduler from '@/modules/Script/ScriptScheduler';

describe('ScriptScheduler', () => {
    beforeEach(() => {
        vi.useFakeTimers();
    });

    it('runs a callback after the requested delay', () => {
        const scheduler = new ScriptScheduler();
        const callback = vi.fn();

        scheduler.scheduleAfter(1000, callback);
        vi.advanceTimersByTime(999);
        expect(callback).not.toHaveBeenCalled();

        vi.advanceTimersByTime(1);
        expect(callback).toHaveBeenCalledTimes(1);
    });

    it('cancels pending callbacks on dispose', () => {
        const scheduler = new ScriptScheduler();
        const callback = vi.fn();

        scheduler.scheduleAfter(1000, callback);
        scheduler.dispose();
        vi.advanceTimersByTime(5000);

        expect(callback).not.toHaveBeenCalled();
        expect(scheduler.isDisposed()).toBe(true);
    });

    it('ignores scheduling after dispose', () => {
        const scheduler = new ScriptScheduler();
        const callback = vi.fn();

        scheduler.dispose();
        scheduler.scheduleAfter(0, callback);
        vi.advanceTimersByTime(1000);

        expect(callback).not.toHaveBeenCalled();
    });

    it('runs registered disposers once on dispose', () => {
        const scheduler = new ScriptScheduler();
        const disposer = vi.fn();

        scheduler.addDisposer(disposer);
        scheduler.dispose();
        scheduler.dispose();

        expect(disposer).toHaveBeenCalledTimes(1);
    });
});
