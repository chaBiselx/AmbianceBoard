import { beforeEach, describe, expect, it, vi } from 'vitest';

const labelMocks = vi.hoisted(() => ({ csrf: vi.fn(), consoleError: vi.fn() }));

vi.mock('@/modules/General/Csrf', () => ({ default: { getToken: labelMocks.csrf } }));
vi.mock('@/modules/General/ConsoleTesteur', () => ({ default: { error: labelMocks.consoleError } }));

const response = (data: object, ok = true) => ({ ok, json: async () => data });
const labels = {
    filename: 'track.mp3',
    bpm: 120,
    duration_seconds: 180,
    categories: {
        low: { category_confidence: 0.2, labels: [{ label: 'quiet', confidence: 0.2 }] },
        high: { category_confidence: 0.9, labels: [{ label: 'dance', confidence: 0.5 }] },
        medium: { category_confidence: 0.6, labels: [{ label: 'warm', confidence: 0.35 }] },
    },
};

describe('MusicLabeler page script', () => {
    beforeEach(() => {
        vi.resetModules();
        vi.clearAllMocks();
        labelMocks.csrf.mockReturnValue('csrf-token');
        document.body.innerHTML = `
            <button id="label-all-btn"></button>
            <span id="progress-counter" class="d-none"></span>
            <span id="progress-current"></span><span id="progress-total"></span>
            <table>
                <tr><td class="label-result" data-music-id="existing" data-labels='${JSON.stringify(labels)}'></td>
                    <button class="label-btn btn-outline-primary" data-music-id="existing" data-url="/existing"></button></tr>
                <tr><td class="label-result" data-music-id="one"></td>
                    <button class="label-btn btn-outline-primary" data-music-id="one" data-url="/one"></button></tr>
                <tr><td class="label-result" data-music-id="error"></td>
                    <button class="label-btn" data-music-id="error" data-url="/error"></button></tr>
                <tr><td class="label-result" data-music-id="network"></td>
                    <button class="label-btn" data-music-id="network" data-url="/network"></button></tr>
            </table>
        `;
    });

    it('renders saved labels, handles analysis outcomes, and tracks batch progress', async () => {
        const fetchMock = vi.fn()
            .mockResolvedValueOnce(response(labels))
            .mockResolvedValueOnce(response({ error: 'No audio' }, false))
            .mockRejectedValueOnce(new Error('offline'))
            .mockResolvedValueOnce(response(labels))
            .mockResolvedValueOnce(response(labels));
        vi.stubGlobal('fetch', fetchMock);
        const consoleError = vi.spyOn(console, 'error').mockImplementation(() => {});
        await import('@/MusicLabeler');
        document.dispatchEvent(new Event('DOMContentLoaded'));

        const saved = document.querySelector<HTMLTableCellElement>('[data-music-id="existing"].label-result')!;
        expect(saved.innerHTML.indexOf('high')).toBeLessThan(saved.innerHTML.indexOf('medium'));
        expect(saved.innerHTML).toContain('bg-success');
        expect(saved.innerHTML).toContain('bg-info');
        expect(saved.innerHTML).toContain('bg-light text-dark');
        expect(document.querySelector<HTMLButtonElement>('[data-music-id="existing"].label-btn')!.classList.contains('btn-outline-success')).toBe(true);

        document.querySelector<HTMLButtonElement>('[data-music-id="one"].label-btn')!.click();
        await vi.waitFor(() => expect(document.querySelector('[data-music-id="one"].label-result')!.innerHTML).toContain('dance'));

        const failedButton = document.querySelector<HTMLButtonElement>('[data-music-id="error"].label-btn')!;
        failedButton.click();
        await vi.waitFor(() => expect(document.querySelector('[data-music-id="error"].label-result')!.textContent).toContain('No audio'));
        expect(failedButton.disabled).toBe(false);

        const networkButton = document.querySelector<HTMLButtonElement>('[data-music-id="network"].label-btn')!;
        networkButton.click();
        await vi.waitFor(() => expect(document.querySelector('[data-music-id="network"].label-result')!.textContent).toContain('Erreur réseau'));
        expect(labelMocks.consoleError).toHaveBeenCalledOnce();

        document.querySelector<HTMLButtonElement>('[data-music-id="existing"].label-btn')!.remove();
        document.querySelector<HTMLButtonElement>('[data-music-id="one"].label-btn')!.remove();
        document.getElementById('label-all-btn')!.click();
        await vi.waitFor(() => expect(document.getElementById('label-all-btn')!.textContent).toContain('Terminé'));

        expect(document.getElementById('progress-counter')!.classList.contains('d-none')).toBe(false);
        expect(document.getElementById('progress-total')!.textContent).toBe('2');
        expect(document.getElementById('progress-current')!.textContent).toBe('2');
        expect(fetchMock).toHaveBeenCalledTimes(5);
        expect(consoleError).not.toHaveBeenCalled();
    });
});