import { beforeEach, describe, expect, it, vi } from 'vitest';

const dimensionMocks = vi.hoisted(() => ({ csrf: vi.fn() }));
vi.mock('@/modules/General/Csrf', () => ({ default: { getToken: dimensionMocks.csrf } }));

describe('UpdateDimension page script', () => {
    beforeEach(() => {
        vi.resetModules();
        vi.clearAllMocks();
        dimensionMocks.csrf.mockReturnValue('csrf-token');
        document.body.innerHTML = `
            <div id="demo-icon" class="icon-dim-175"></div>
            <div class="block-update" data-url="/dimension" data-type="icon">
                <button class="btn-increase"></button>
                <button class="btn-decrease"></button>
            </div>
        `;
    });

    it('clamps dimension changes and persists each actual update', async () => {
        const fetchMock = vi.fn();
        vi.stubGlobal('fetch', fetchMock);
        await import('@/UpdateDimension');
        document.dispatchEvent(new Event('DOMContentLoaded'));
        const demo = document.getElementById('demo-icon')!;
        const increase = document.querySelector<HTMLButtonElement>('.btn-increase')!;
        const decrease = document.querySelector<HTMLButtonElement>('.btn-decrease')!;

        increase.click();
        expect(demo.classList.contains('icon-dim-200')).toBe(true);
        expect(fetchMock).toHaveBeenLastCalledWith('/dimension', expect.objectContaining({ body: JSON.stringify({ dim: 200 }) }));
        increase.click();
        expect(fetchMock).toHaveBeenCalledOnce();

        decrease.click();
        expect(demo.classList.contains('icon-dim-175')).toBe(true);
        for (let step = 0; step < 5; step++) decrease.click();
        expect(demo.classList.contains('icon-dim-50')).toBe(true);
        const callsAtMinimum = fetchMock.mock.calls.length;
        decrease.click();
        expect(fetchMock).toHaveBeenCalledTimes(callsAtMinimum);
        expect(fetchMock).toHaveBeenCalledWith('/dimension', expect.objectContaining({
            method: 'UPDATE',
            headers: { 'X-CSRFToken': 'csrf-token' },
        }));
    });
});