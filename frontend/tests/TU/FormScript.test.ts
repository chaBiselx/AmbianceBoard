import { beforeEach, describe, expect, it, vi } from 'vitest';

const scriptMocks = vi.hoisted(() => ({ csrf: vi.fn(), notify: vi.fn() }));
vi.mock('@/modules/General/Csrf', () => ({ default: { getToken: scriptMocks.csrf } }));
vi.mock('@/modules/General/Notifications', () => ({ default: { createClientNotification: scriptMocks.notify } }));

const stepsMarkup = `
    <div id="script-steps" data-url-save="/save" data-url-reorder="/reorder"
        data-params-by-action='{"SET_VOLUME":["volume"],"PLAY_TRACK":["track"]}'>
        <form id="script-step-form">
            <select id="step-action-type"><option value="SET_VOLUME" selected>Volume</option><option value="PLAY_TRACK">Track</option></select>
            <select id="step-trigger-type"><option value="ON_STEP_END" selected>End</option><option value="ON_CLICK">Click</option></select>
            <div id="step-source-wrapper"></div>
            <div class="script-param" data-param="volume"></div><div class="script-param" data-param="track"></div>
        </form>
        <div id="script-step-list">
            <div data-step-uuid="step-1"><button class="step-move" data-direction="-1"></button><button class="step-move" data-direction="1"></button><button class="step-delete" data-url-delete="/step-delete"></button></div>
            <div data-step-uuid="step-2"><button class="step-move" data-direction="-1"></button><button class="step-move" data-direction="1"></button></div>
        </div>
    </div>
`;

describe('FormScript page script', () => {
    beforeEach(() => {
        vi.resetModules();
        vi.clearAllMocks();
        scriptMocks.csrf.mockReturnValue('csrf-token');
        document.body.innerHTML = `
            <div id="script-editor" data-url-create="/create"></div>
            <form id="script-create-form"></form>
            <div id="script-listing">
                <div data-script-uuid="script-1" data-url-steps="/steps" data-url-update="/script-update" data-url-delete="/script-delete">
                    <button class="script-select"></button>
                    <input class="script-enabled" type="checkbox">
                    <button class="script-delete"></button>
                </div>
            </div>
            <div id="script-steps-panel"></div>
        `;
    });

    it('loads steps, updates visibility, saves and reorders them, and reports failed mutations', async () => {
        const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
            const url = String(input);
            if (url === '/steps' && init?.method === 'GET') return { text: async () => stepsMarkup } as Response;
            if (url === '/steps') return { text: async () => stepsMarkup } as Response;
            if (url === '/reorder') return { ok: true } as Response;
            if (url === '/save' || url === '/step-delete' || url === '/script-update') return { ok: true } as Response;
            if (url === '/create') return { ok: false, json: async () => ({ error: 'Name already used' }) } as Response;
            if (url === '/script-delete') return { ok: false, json: async () => ({ error: 'Cannot delete' }) } as Response;
            throw new Error(`Unexpected ${init?.method} ${url}`);
        });
        vi.stubGlobal('fetch', fetchMock);
        await import('@/FormScript');
        document.dispatchEvent(new Event('DOMContentLoaded'));

        const createForm = document.getElementById('script-create-form')!;
        createForm.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }));
        await vi.waitFor(() => expect(scriptMocks.notify).toHaveBeenCalledWith({ message: 'Name already used', type: 'error' }));

        const enabled = document.querySelector<HTMLInputElement>('.script-enabled')!;
        enabled.checked = true;
        enabled.dispatchEvent(new Event('change', { bubbles: true }));
        await vi.waitFor(() => expect(fetchMock).toHaveBeenCalledWith('/script-update', expect.objectContaining({ method: 'POST' })));

        document.querySelector<HTMLButtonElement>('.script-select')!.click();
        await vi.waitFor(() => expect(document.getElementById('script-step-list')).not.toBeNull());
        const volumeField = document.querySelector<HTMLElement>('[data-param="volume"]')!;
        const trackField = document.querySelector<HTMLElement>('[data-param="track"]')!;
        const sourceWrapper = document.getElementById('step-source-wrapper')!;
        expect(volumeField.hidden).toBe(false);
        expect(trackField.hidden).toBe(true);
        expect(sourceWrapper.hidden).toBe(false);
        document.getElementById('step-action-type')!.dispatchEvent(new Event('change'));
        (document.getElementById('step-trigger-type') as HTMLSelectElement).value = 'ON_CLICK';
        document.getElementById('step-trigger-type')!.dispatchEvent(new Event('change'));
        expect(sourceWrapper.hidden).toBe(true);

        document.getElementById('script-step-form')!.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }));
        await vi.waitFor(() => expect(fetchMock).toHaveBeenCalledWith('/save', expect.objectContaining({ method: 'POST' })));

        const firstStep = document.querySelector<HTMLElement>('[data-step-uuid="step-1"]')!;
        firstStep.querySelector<HTMLButtonElement>('.step-move[data-direction="-1"]')!.click();
        expect(fetchMock).not.toHaveBeenCalledWith('/reorder', expect.anything());
        firstStep.querySelector<HTMLButtonElement>('.step-move[data-direction="1"]')!.click();
        await vi.waitFor(() => expect(fetchMock).toHaveBeenCalledWith('/reorder', expect.objectContaining({
            body: JSON.stringify({ steps: ['step-2', 'step-1'] }),
        })));

        document.querySelector<HTMLButtonElement>('.step-delete')!.click();
        await vi.waitFor(() => expect(fetchMock).toHaveBeenCalledWith('/step-delete', expect.objectContaining({ method: 'DELETE' })));
        document.querySelector<HTMLButtonElement>('.script-delete')!.click();
        await vi.waitFor(() => expect(scriptMocks.notify).toHaveBeenCalledWith({ message: 'Cannot delete', type: 'error' }));
    });
});