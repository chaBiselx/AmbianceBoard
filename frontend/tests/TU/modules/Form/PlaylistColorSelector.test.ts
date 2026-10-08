import { beforeEach, describe, expect, it, vi } from 'vitest';
import { initializePlaylistColorSelector, PlaylistColorSelectorDependencies } from '@/modules/Form/PlaylistColorSelector';

describe('PlaylistColorSelector', () => {
    beforeEach(() => {
        document.body.innerHTML = `
            <button id="btn-select-other-color" data-url="/playlist-colors"></button>
            <input id="id_color">
            <input id="id_colorText">
            <div id="modal-body"></div>
        `;
    });

    it('lists available colors and applies the selected color', async () => {
        const responseBody = {
            default_playlists: [{ color: '#123456', colorText: '#ffffff', typePlaylist: '<img src=x onerror=alert(1)>' }],
            unique_playlists: [],
        };
        const dependencies: PlaylistColorSelectorDependencies = {
            fetch: vi.fn().mockResolvedValue({ json: async () => responseBody } as Response),
            showModal: vi.fn(options => {
                document.getElementById('modal-body')!.innerHTML = options.body;
                options.callback?.();
            }),
            hideModal: vi.fn(),
            renderPreview: vi.fn(),
            log: vi.fn(),
            error: vi.fn(),
        };
        initializePlaylistColorSelector(dependencies);

        document.getElementById('btn-select-other-color')!.dispatchEvent(new Event('click', { bubbles: true }));

        await vi.waitFor(() => expect(dependencies.showModal).toHaveBeenCalled());
        expect(dependencies.fetch).toHaveBeenCalledWith('/playlist-colors', { method: 'GET' });
        expect(document.querySelector('#modal-body .col-5 small')?.textContent).toBe('<img src=x onerror=alert(1)>');
        expect(document.querySelector('#modal-body img')).toBeNull();

        document.querySelector<HTMLButtonElement>('.btn-select-playlist-color')!.click();

        expect(document.getElementById<HTMLInputElement>('id_color')!.value).toBe('#123456');
        expect(document.getElementById<HTMLInputElement>('id_colorText')!.value).toBe('#ffffff');
        expect(dependencies.hideModal).toHaveBeenCalledOnce();
        expect(dependencies.renderPreview).toHaveBeenCalledWith(document);
    });
});