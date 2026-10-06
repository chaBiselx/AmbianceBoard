import { beforeEach, describe, expect, it, vi } from 'vitest';
import { initializePlaylistEntityActions, PlaylistEntityActionDependencies } from '@/modules/Form/PlaylistEntityActions';

describe('PlaylistEntityActions', () => {
    beforeEach(() => {
        document.body.innerHTML = `
            <button id="btn-delete-playlist" data-deleteurl="/playlists/1" data-redirecturl="/playlists"></button>
            <button class="btn-delete-music" data-deleteurl="/music/2" data-redirecturl="/playlists/1"></button>
        `;
    });

    it('deletes and redirects after confirmation', async () => {
        const dependencies: PlaylistEntityActionDependencies = {
            fetch: vi.fn().mockResolvedValue({ status: 200 } as Response),
            getCsrfToken: vi.fn().mockReturnValue('csrf-token'),
            confirm: vi.fn().mockReturnValue(true),
            redirect: vi.fn(),
            error: vi.fn(),
        };
        initializePlaylistEntityActions(dependencies);

        document.getElementById('btn-delete-playlist')!.dispatchEvent(new Event('click', { bubbles: true }));
        await vi.waitFor(() => expect(dependencies.redirect).toHaveBeenCalledWith('/playlists'));

        expect(dependencies.fetch).toHaveBeenCalledWith('/playlists/1', {
            method: 'DELETE',
            headers: { 'X-CSRFToken': 'csrf-token' },
        });
        expect(dependencies.error).not.toHaveBeenCalled();
    });

    it('does not request deletion when confirmation is declined', () => {
        const dependencies: PlaylistEntityActionDependencies = {
            fetch: vi.fn(),
            getCsrfToken: vi.fn(),
            confirm: vi.fn().mockReturnValue(false),
            redirect: vi.fn(),
            error: vi.fn(),
        };
        initializePlaylistEntityActions(dependencies);

        document.querySelector<HTMLButtonElement>('.btn-delete-music')!.click();

        expect(dependencies.confirm).toHaveBeenCalledWith('Êtes-vous sûr de vouloir supprimer la musique ?');
        expect(dependencies.fetch).not.toHaveBeenCalled();
    });
});