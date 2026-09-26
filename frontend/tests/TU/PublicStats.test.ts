import { beforeEach, describe, expect, it, vi } from 'vitest';

const graphMocks = vi.hoisted(() => ({
    lineArgs: [] as unknown[],
    barArgs: [] as unknown[],
    lineInit: vi.fn(),
    barInit: vi.fn(),
}));

vi.mock('@/modules/Chart/DashboardLineGraph', () => ({
    DashboardLineGraph: class {
        constructor(...args: unknown[]) { graphMocks.lineArgs = args; }
        init() { graphMocks.lineInit(); }
    },
}));

vi.mock('@/modules/Chart/DashboardBarGraph', () => ({
    DashboardBarGraph: class {
        constructor(...args: unknown[]) { graphMocks.barArgs = args; }
        init() { graphMocks.barInit(); }
    },
}));

describe('PublicStats page script', () => {
    beforeEach(() => {
        vi.resetModules();
        vi.clearAllMocks();
        graphMocks.lineArgs = [];
        graphMocks.barArgs = [];
    });

    it('initializes the user activity line and session duration bar graphs', async () => {
        await import('@/PublicStats');
        document.dispatchEvent(new Event('DOMContentLoaded'));

        expect(graphMocks.lineArgs).toEqual(['user-frequentation', 'periode-chart']);
        expect(graphMocks.barArgs).toEqual(['user-average-session-duration', 'periode-chart']);
        expect(graphMocks.lineInit).toHaveBeenCalledOnce();
        expect(graphMocks.barInit).toHaveBeenCalledOnce();
    });
});