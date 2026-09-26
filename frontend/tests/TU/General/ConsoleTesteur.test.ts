import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';

vi.mock('@/modules/General/ConsoleCustom', () => ({
    default: {
        assert: vi.fn(),
        clear: vi.fn(),
        count: vi.fn(),
        countReset: vi.fn(),
        debug: vi.fn(),
        dir: vi.fn(),
        dirxml: vi.fn(),
        error: vi.fn(),
        group: vi.fn(),
        groupCollapsed: vi.fn(),
        groupEnd: vi.fn(),
        info: vi.fn(),
        log: vi.fn(),
        table: vi.fn(),
        time: vi.fn(),
        timeEnd: vi.fn(),
        timeLog: vi.fn(),
        timeStamp: vi.fn(),
        trace: vi.fn(),
        warn: vi.fn(),
    },
}));

describe('ConsoleTesteur with the DOM present', () => {
    let consoleTesteur: (typeof import('../../../src/modules/General/ConsoleTesteur'))['default'];
    let clearButton: HTMLButtonElement;

    beforeEach(async () => {
        vi.resetModules();
        document.body.innerHTML = `
            <div id="console-testeur"></div>
            <button id="clear-console-testeur"></button>
        `;
        clearButton = document.getElementById('clear-console-testeur') as HTMLButtonElement;
        const module = await import('../../../src/modules/General/ConsoleTesteur');
        consoleTesteur = module.default;
    });

    afterEach(() => {
        vi.restoreAllMocks();
    });

    it('should render logged messages in the DOM', () => {
        consoleTesteur.log('hello');
        const dom = document.getElementById('console-testeur')!;
        expect(dom.textContent).toContain('hello');
    });

    it('should clear the console when the clear button is clicked', () => {
        consoleTesteur.log('hello');
        clearButton.dispatchEvent(new Event('click'));
        expect(document.getElementById('console-testeur')!.innerHTML).toBe('');
    });

    it('should clear the console directly', () => {
        consoleTesteur.log('hello');
        consoleTesteur.clear();
        expect(document.getElementById('console-testeur')!.innerHTML).toBe('');
    });

    it('should render an assertion failure and not render a passing assertion', () => {
        consoleTesteur.assert(false, 'failed');
        expect(document.getElementById('console-testeur')!.textContent).toContain('Assertion failed');

        document.getElementById('console-testeur')!.innerHTML = '';
        consoleTesteur.assert(true, 'ok');
        expect(document.getElementById('console-testeur')!.innerHTML).toBe('');
    });

    it('should count and reset counters', () => {
        consoleTesteur.count('c');
        consoleTesteur.count('c');
        expect(document.getElementById('console-testeur')!.textContent).toContain('c: 2');

        consoleTesteur.countReset('c');
        expect(document.getElementById('console-testeur')!.textContent).toContain('c: 0');
    });

    it('should format object and primitive values with dir', () => {
        consoleTesteur.dir({ a: 1 });
        consoleTesteur.dir(42);
        const text = document.getElementById('console-testeur')!.textContent;
        expect(text).toContain('"a": 1');
        expect(text).toContain('42');
    });

    it('should render dirxml, debug, info and error entries', () => {
        consoleTesteur.dirxml('x');
        consoleTesteur.debug('d');
        consoleTesteur.info('i');
        consoleTesteur.error('e');
        const text = document.getElementById('console-testeur')!.textContent;
        expect(text).toContain('x');
        expect(text).toContain('d');
        expect(text).toContain('i');
        expect(text).toContain('e');
    });

    it('should indent nested groups and unindent on groupEnd', () => {
        consoleTesteur.group('outer');
        consoleTesteur.log('inner');
        consoleTesteur.groupEnd();
        consoleTesteur.group();
        consoleTesteur.groupCollapsed('collapsed');
        consoleTesteur.groupEnd();
        consoleTesteur.groupEnd();
        consoleTesteur.groupEnd();

        const text = document.getElementById('console-testeur')!.textContent;
        expect(text).toContain('▼ outer');
        expect(text).toContain('▶ collapsed');
    });

    it('should render a table from an array with explicit properties', () => {
        consoleTesteur.table([{ a: 1, b: 2 }], ['a']);
        expect(document.getElementById('console-testeur')!.textContent).toContain('0: 1');
    });

    it('should render a table from an array without explicit properties', () => {
        consoleTesteur.table([{ a: 1, b: 2 }]);
        expect(document.getElementById('console-testeur')!.textContent).toContain('0: 1 | 2');
    });

    it('should render non-array table data using formatData', () => {
        consoleTesteur.table({ a: 1 });
        expect(document.getElementById('console-testeur')!.textContent).toContain('"a": 1');
    });

    it('should measure elapsed time between time and timeEnd', () => {
        consoleTesteur.time('t');
        consoleTesteur.timeEnd('t');
        expect(document.getElementById('console-testeur')!.textContent).toContain('t:');
    });

    it('should report a missing timer on timeEnd', () => {
        consoleTesteur.timeEnd('missing');
        expect(document.getElementById('console-testeur')!.textContent).toContain("Timer 'missing' does not exist");
    });

    it('should log intermediate time with and without extra data', () => {
        consoleTesteur.time('t2');
        consoleTesteur.timeLog('t2');
        consoleTesteur.timeLog('t2', 'extra');
        expect(document.getElementById('console-testeur')!.textContent).toContain('t2:');
    });

    it('should report a missing timer on timeLog', () => {
        consoleTesteur.timeLog('missing');
        expect(document.getElementById('console-testeur')!.textContent).toContain("Timer 'missing' does not exist");
    });

    it('should render a timestamp with and without a label', () => {
        consoleTesteur.timeStamp('label');
        consoleTesteur.timeStamp();
        const text = document.getElementById('console-testeur')!.textContent;
        expect(text).toContain('label @');
        expect(text).toContain('Timestamp @');
    });

    it('should render a trace with and without data', () => {
        consoleTesteur.trace('trace message');
        consoleTesteur.trace();
        expect(document.getElementById('console-testeur')!.textContent).toContain('trace message');
    });

    it('should render a warning', () => {
        consoleTesteur.warn('warn message');
        expect(document.getElementById('console-testeur')!.textContent).toContain('warn message');
    });

    it('should fall back to String() when JSON.stringify fails on circular data', () => {
        const circular: any = {};
        circular.self = circular;
        consoleTesteur.log(circular);
        expect(document.getElementById('console-testeur')!.textContent).toContain('[object Object]');
    });
});

describe('ConsoleTesteur without the DOM', () => {
    let consoleTesteur: (typeof import('../../../src/modules/General/ConsoleTesteur'))['default'];

    beforeEach(async () => {
        vi.resetModules();
        document.body.innerHTML = '';
        const module = await import('../../../src/modules/General/ConsoleTesteur');
        consoleTesteur = module.default;
    });

    it('should not throw when writing to a missing DOM', () => {
        expect(() => {
            consoleTesteur.log('hello');
            consoleTesteur.clear();
            consoleTesteur.groupEnd();
        }).not.toThrow();
    });
});
