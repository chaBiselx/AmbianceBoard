import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

const dashboardMocks = vi.hoisted(() => ({
    graph: vi.fn(),
    init: vi.fn(),
    notify: vi.fn(),
    warn: vi.fn(),
}));

vi.mock('@/modules/Chart/DashboardLineGraph', () => ({
    DashboardLineGraph: class {
        constructor(id: string, period: string) {
            dashboardMocks.graph(id, period);
        }

        init() {
            dashboardMocks.init();
        }
    },
}));

vi.mock('@/modules/General/Notifications', () => ({
    default: { createClientNotification: dashboardMocks.notify },
}));

vi.mock('@/modules/General/ConsoleCustom', () => ({
    default: { warn: dashboardMocks.warn },
}));

import '@/ManagerDashboard';

describe('ManagerDashboard home share link', () => {
    const writeText = vi.fn();
    let sourceSelect: HTMLSelectElement;
    let urlInput: HTMLInputElement;
    let copyButton: HTMLButtonElement;

    function initialize() {
        document.dispatchEvent(new Event('DOMContentLoaded'));
    }

    function selectSource(source: string) {
        sourceSelect.value = source;
        sourceSelect.dispatchEvent(new Event('change'));
    }

    beforeEach(() => {
        vi.clearAllMocks();
        writeText.mockReset().mockResolvedValue(undefined);
        vi.stubGlobal('navigator', { clipboard: { writeText } });
        document.body.innerHTML = `
            <select id="home-share-source" data-home-url="https://example.test/">
                <option value="">Choisir une source</option>
                <option value="google">google</option>
                <option value="newsletter">newsletter</option>
            </select>
            <input id="home-share-url" readonly>
            <button id="home-share-copy" class="share-link-btn" disabled></button>
        `;
        sourceSelect = document.querySelector<HTMLSelectElement>('#home-share-source')!;
        urlInput = document.querySelector<HTMLInputElement>('#home-share-url')!;
        copyButton = document.querySelector<HTMLButtonElement>('#home-share-copy')!;
    });

    afterEach(() => {
        vi.unstubAllGlobals();
        document.body.innerHTML = '';
    });

    it('initializes all graphs and copies the home URL with an empty source', async () => {
        initialize();

        expect(dashboardMocks.graph.mock.calls).toEqual([
            ['evolution-user', 'periode-chart'],
            ['activity-user', 'periode-chart'],
            ['activity-errors', 'periode-chart'],
            ['activity-referer', 'periode-chart'],
            ['activity-utm-source', 'periode-chart'],
        ]);
        expect(dashboardMocks.init).toHaveBeenCalledTimes(5);
        expect(urlInput.value).toBe('https://example.test/?utm_source=');
        expect(copyButton.disabled).toBe(false);
        expect(copyButton.dataset.url).toBe(urlInput.value);
        copyButton.click();
        await vi.waitFor(() => expect(writeText).toHaveBeenCalledExactlyOnceWith(urlInput.value));
    });

    it('handles missing share controls without breaking the graphs', () => {
        document.body.innerHTML = '';

        expect(initialize).not.toThrow();
        expect(dashboardMocks.init).toHaveBeenCalledTimes(5);
    });

    it('handles an absent home URL', () => {
        delete sourceSelect.dataset.homeUrl;
        expect(initialize).not.toThrow();
        expect(copyButton.disabled).toBe(true);
    });

    it('keeps an empty source list disabled but allows copying the home URL', () => {
        sourceSelect.innerHTML = '<option value="">Aucune source UTM disponible</option>';
        sourceSelect.disabled = true;
        initialize();

        expect(sourceSelect.disabled).toBe(true);
        expect(urlInput.value).toBe('https://example.test/?utm_source=');
        expect(copyButton.disabled).toBe(false);
    });

    it('generates the home URL and copies the latest selected source', async () => {
        initialize();
        selectSource('google');
        expect(urlInput.value).toBe('https://example.test/?utm_source=google');
        selectSource('newsletter');
        expect(copyButton.disabled).toBe(false);
        expect(copyButton.dataset.url).toBe(urlInput.value);
        copyButton.click();

        await vi.waitFor(() => {
            expect(writeText).toHaveBeenCalledExactlyOnceWith('https://example.test/?utm_source=newsletter');
            expect(dashboardMocks.notify).toHaveBeenCalledWith({
                message: 'Lien copi\u00e9 dans le presse-papiers',
                type: 'success',
            });
        });
    });

    it('encodes source values without changing them or injecting query parameters', () => {
        const source = ' partenaire \u00e9t\u00e9 & + # ? / = ';
        sourceSelect.add(new Option(source, source));
        initialize();
        selectSource(source);

        const url = new URL(urlInput.value);
        expect(url.origin).toBe('https://example.test');
        expect(url.pathname).toBe('/');
        expect([...url.searchParams.entries()]).toEqual([['utm_source', source]]);
        expect(url.hash).toBe('');
        expect(copyButton.dataset.url).toBe(urlInput.value);
    });

    it.each(['', 'unknown'])('keeps the empty-source link copyable when selecting "%s"', (source: string) => {
        initialize();
        selectSource('google');
        selectSource(source);

        expect(urlInput.value).toBe('https://example.test/?utm_source=');
        expect(copyButton.dataset.url).toBe(urlInput.value);
        expect(copyButton.disabled).toBe(false);
    });

    it('allows manual selection when the clipboard API is unavailable', () => {
        vi.stubGlobal('navigator', {});
        initialize();
        selectSource('google');
        urlInput.click();

        expect(urlInput.value).toBe('https://example.test/?utm_source=google');
        expect(copyButton.disabled).toBe(true);
        expect(urlInput.selectionStart).toBe(0);
        expect(urlInput.selectionEnd).toBe(urlInput.value.length);
        expect(writeText).not.toHaveBeenCalled();
    });

    it('reports clipboard errors while leaving the link selectable', async () => {
        writeText.mockRejectedValue(new Error('blocked'));
        initialize();
        selectSource('google');
        copyButton.click();

        await vi.waitFor(() => expect(dashboardMocks.notify).toHaveBeenCalledWith({
            message: 'Impossible de copier le lien',
            type: 'danger',
        }));
        expect(urlInput.value).toBe('https://example.test/?utm_source=google');
    });
});