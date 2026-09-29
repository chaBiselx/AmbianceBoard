import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import ConsoleTraceServeur from '../../../src/modules/General/ConsoleTraceServeur';
import Csrf from '../../../src/modules/General/Csrf';
import Config from '../../../src/modules/General/Config';

vi.mock('@/modules/General/Csrf', () => ({
    default: { getToken: vi.fn() },
}));

vi.mock('@/modules/General/Config', () => ({
    default: { DEBUG: false, SOUNDBOARD_DIV_ID_PLAYERS: 'players' },
}));

describe('ConsoleTraceServeur', () => {
    beforeEach(() => {
        vi.mocked(Csrf.getToken).mockReturnValue('csrf-token');
        globalThis.fetch = vi.fn().mockResolvedValue({});
    });

    afterEach(() => {
        vi.restoreAllMocks();
    });

    it.each(['debug', 'error', 'info', 'log', 'trace', 'warn'] as const)(
        'sends a trace to the server for %s',
        (level) => {
            (ConsoleTraceServeur as any)[level]('message');
            expect(globalThis.fetch).toHaveBeenCalledWith(
                expect.stringContaining('/trace-front'),
                expect.objectContaining({
                    method: 'POST',
                    headers: expect.objectContaining({ 'X-CSRFToken': 'csrf-token' }),
                })
            );
            const body = JSON.parse((globalThis.fetch as any).mock.calls[0][1].body);
            expect(body.level).toBe(level);
            expect(body.messages[0]).toBe('message');
        }
    );

    it('does not send a trace when the csrf token is missing', () => {
        vi.mocked(Csrf.getToken).mockReturnValue(null);
        ConsoleTraceServeur.log('message');
        expect(globalThis.fetch).not.toHaveBeenCalled();
    });

    it('logs the fetch error when DEBUG is enabled', async () => {
        (Config as any).DEBUG = true;
        globalThis.fetch = vi.fn().mockRejectedValue(new Error('network error'));
        const spy = vi.spyOn(console, 'error').mockImplementation(() => {});

        ConsoleTraceServeur.log('message');
        await new Promise((resolve) => setTimeout(resolve, 0));

        expect(spy).toHaveBeenCalledWith('Failed to send trace to server:', expect.any(Error));
    });

    it('does not log the fetch error when DEBUG is disabled', async () => {
        (Config as any).DEBUG = false;
        globalThis.fetch = vi.fn().mockRejectedValue(new Error('network error'));
        const spy = vi.spyOn(console, 'error').mockImplementation(() => {});

        ConsoleTraceServeur.log('message');
        await new Promise((resolve) => setTimeout(resolve, 0));

        expect(spy).not.toHaveBeenCalled();
    });

    it('runs the no-op methods without throwing', () => {
        expect(() => {
            ConsoleTraceServeur.assert(true, 'a');
            ConsoleTraceServeur.clear();
            ConsoleTraceServeur.count('c');
            ConsoleTraceServeur.countReset('c');
            ConsoleTraceServeur.dir({});
            ConsoleTraceServeur.dirxml('a');
            ConsoleTraceServeur.group('g');
            ConsoleTraceServeur.groupCollapsed('g');
            ConsoleTraceServeur.groupEnd();
            ConsoleTraceServeur.table([]);
            ConsoleTraceServeur.time('t');
            ConsoleTraceServeur.timeEnd('t');
            ConsoleTraceServeur.timeLog('t');
            ConsoleTraceServeur.timeStamp('t');
        }).not.toThrow();
    });
});
