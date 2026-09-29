import { beforeEach, describe, expect, it, vi } from 'vitest';

const copyMocks = vi.hoisted(() => ({
    createPlayer: vi.fn(),
    notify: vi.fn(),
    csrf: vi.fn(),
}));

vi.mock('@/modules/Audio/PlayerCustom', () => ({
    PlayerCustomFactory: { create: copyMocks.createPlayer },
}));
vi.mock('@/modules/General/Notifications', () => ({ default: { createClientNotification: copyMocks.notify } }));
vi.mock('@/modules/General/Csrf', () => ({ default: { getToken: copyMocks.csrf } }));

describe('PlaylistCopiable page script', () => {
    beforeEach(() => {
        vi.resetModules();
        vi.clearAllMocks();
        copyMocks.csrf.mockReturnValue('csrf-token');
        document.body.innerHTML = `
            <button class="playlist-copiable"><span data-playlist-uuid="playlist-1">Preview</span></button>
            <div id="preview-playlist-div" data-url-preview="/preview"></div>
            <div id="previewPlaylist"></div>
        `;
    });

    it('loads a preview and handles all duplicate response outcomes', async () => {
        const duplicateResponses = [
            { ok: true, status: 200, json: async () => ({ success: true, message: 'Duplicated' }) },
            { ok: false, status: 409, json: async () => ({ error: 'Already duplicated' }) },
            { ok: false, status: 500, json: async () => ({}) },
        ];
        const fetchMock = vi.fn(async (url: string) => {
            if (url.startsWith('/preview')) {
                return {
                    text: async () => `
                        <button id="duplicate-playlist-button-with-edition" data-is-edition="true">Edit</button>
                        <button id="duplicate-playlist-button-without-edition" data-url-duplication="/duplicate">Copy</button>
                    `,
                };
            }
            if (url === '/duplicate') return duplicateResponses.shift()!;
            throw new Error('offline');
        });
        vi.stubGlobal('fetch', fetchMock);
        const consoleError = vi.spyOn(console, 'error').mockImplementation(() => {});
        await import('@/PlaylistCopiable');
        document.dispatchEvent(new Event('DOMContentLoaded'));
        document.querySelector<HTMLElement>('[data-playlist-uuid]')!.click();

        await vi.waitFor(() => expect(document.getElementById('duplicate-playlist-button-with-edition')).not.toBeNull());
        expect(fetchMock).toHaveBeenCalledWith('/preview?playlistUuid=playlist-1');
        expect(copyMocks.createPlayer).toHaveBeenCalledOnce();

        const editionButton = document.getElementById('duplicate-playlist-button-with-edition')!;
        const copyButton = document.getElementById('duplicate-playlist-button-without-edition')!;
        editionButton.click();
        await vi.waitFor(() => expect(copyMocks.notify).toHaveBeenCalledWith({ message: 'Duplicated', type: 'success' }));
        expect(fetchMock).toHaveBeenLastCalledWith('/duplicate', expect.objectContaining({
            method: 'POST',
            headers: { 'X-CSRFToken': 'csrf-token' },
        }));

        editionButton.removeAttribute('disabled');
        copyButton.removeAttribute('disabled');
        copyButton.click();
        await vi.waitFor(() => expect(copyMocks.notify).toHaveBeenCalledWith({ message: 'Already duplicated', type: 'warning' }));

        editionButton.removeAttribute('disabled');
        copyButton.removeAttribute('disabled');
        copyButton.click();
        await vi.waitFor(() => expect(copyMocks.notify).toHaveBeenCalledWith({
            message: 'Une erreur inattendue est survenue',
            type: 'error',
        }));

        editionButton.removeAttribute('disabled');
        copyButton.removeAttribute('disabled');
        copyButton.click();
        await vi.waitFor(() => expect(copyMocks.notify).toHaveBeenCalledWith({
            message: 'Erreur de communication avec le serveur',
            type: 'error',
        }));
        expect(consoleError).toHaveBeenCalled();
    });
});