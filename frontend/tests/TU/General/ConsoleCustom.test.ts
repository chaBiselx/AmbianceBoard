import { describe, it, expect, vi, afterEach } from 'vitest';
import ConsoleCustom from '../../../src/modules/General/ConsoleCustom';
import Config from '../../../src/modules/General/Config';

vi.mock('@/modules/General/Config', () => ({
    default: { DEBUG: false, SOUNDBOARD_DIV_ID_PLAYERS: 'players' },
}));

type Method = { name: keyof Console; args: any[] };

const methods: Method[] = [
    { name: 'assert', args: [true, 'assertion'] },
    { name: 'clear', args: [] },
    { name: 'count', args: ['label'] },
    { name: 'countReset', args: ['label'] },
    { name: 'debug', args: ['debug message'] },
    { name: 'dir', args: [{ a: 1 }, { depth: 1 }] },
    { name: 'dirxml', args: ['xml'] },
    { name: 'error', args: ['error message'] },
    { name: 'group', args: ['group'] },
    { name: 'groupCollapsed', args: ['group collapsed'] },
    { name: 'groupEnd', args: [] },
    { name: 'info', args: ['info message'] },
    { name: 'log', args: ['log message'] },
    { name: 'table', args: [[{ a: 1 }], ['a']] },
    { name: 'time', args: ['timer'] },
    { name: 'timeEnd', args: ['timer'] },
    { name: 'timeLog', args: ['timer', 'extra'] },
    { name: 'timeStamp', args: ['stamp'] },
    { name: 'trace', args: ['trace message'] },
    { name: 'warn', args: ['warn message'] },
];

describe('ConsoleCustom', () => {
    afterEach(() => {
        vi.restoreAllMocks();
        delete (console as any).timeStamp;
    });

    it.each(methods)('forwards $name to the native console when DEBUG is true', ({ name, args }) => {
        (Config as any).DEBUG = true;
        // Node's console has no native timeStamp method, so it can't be spied on.
        if (!(name in console)) {
            (console as any)[name] = () => {};
        }
        const spy = vi.spyOn(console, name as any).mockImplementation(() => {});
        (ConsoleCustom as any)[name](...args);
        expect(spy).toHaveBeenCalledWith(...args);
    });

    it.each(methods)('does not forward $name to the native console when DEBUG is false', ({ name, args }) => {
        (Config as any).DEBUG = false;
        if (!(name in console)) {
            (console as any)[name] = () => {};
        }
        const spy = vi.spyOn(console, name as any).mockImplementation(() => {});
        (ConsoleCustom as any)[name](...args);
        expect(spy).not.toHaveBeenCalled();
    });
});
