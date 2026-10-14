import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { CommunityPlaylistAdder } from '@/modules/SoundboardOrganizer/CommunityPlaylistAdder';

const communityMocks = vi.hoisted(() => ({
    getToken: vi.fn(),
    showModal: vi.fn(),
    hideModal: vi.fn(),
    createPlayers: vi.fn(),
    notify: vi.fn(),
    reload: vi.fn(),
}));

vi.mock('@/modules/Audio/PlayerCustom', () => ({
    PlayerCustomFactory: { create: communityMocks.createPlayers },
}));
vi.mock('@/modules/General/Csrf', () => ({ default: { getToken: communityMocks.getToken } }));
vi.mock('@/modules/General/Notifications', () => ({
    default: { createClientNotification: communityMocks.notify },
}));
vi.mock('@/modules/General/Modal', () => ({
    default: {
        getMainHTMLElement: () => document.getElementById('mainModal'),
        getInstance: () => ({ hide: communityMocks.hideModal }),
        show: communityMocks.showModal,
    },
}));

describe('CommunityPlaylistAdder', () => {
    beforeEach(() => {
        vi.clearAllMocks();
        communityMocks.getToken.mockReturnValue('csrf-token');
        communityMocks.createPlayers.mockReturnValue([]);
        communityMocks.showModal.mockImplementation((options: { body: string }) => {
            document.getElementById('mainModalBody')!.innerHTML = options.body;
        });
        vi.stubGlobal('location', { origin: 'http://localhost', reload: communityMocks.reload });
        document.body.innerHTML = `
            <button id="add-community-playlist-button"
                data-url-list="/community-playlists?target=library"
                data-modal-title="Add a community button"
                data-loading-message="Loading"
                data-load-error="Could not load"
                data-add-error="Could not add"
                data-csrf-error="Invalid request"></button>
            <div id="mainModal"><div id="mainModalBody"></div></div>
        `;
    });

    afterEach(() => {
        vi.unstubAllGlobals();
    });

    it('loads community playlists and copies the selected playlist to the user library', async () => {
        const fetchMock = vi.fn(async (_input: RequestInfo | URL, init?: RequestInit) => {
            if (init?.method === 'GET') {
                return {
                    ok: true,
                    redirected: false,
                    text: async () => '<button class="btn-edit-mode-duplicate" data-url-duplication="/duplicate"></button>',
                } as Response;
            }
            return {
                ok: true,
                json: async () => ({ success: true }),
            } as Response;
        });
        vi.stubGlobal('fetch', fetchMock);

        new CommunityPlaylistAdder().addEvent();
        document.getElementById('add-community-playlist-button')!.click();

        await vi.waitFor(() => {
            const button = document.querySelector<HTMLButtonElement>('.btn-edit-mode-duplicate');
            expect(button).not.toBeNull();
        });
        const duplicateButton = document.querySelector<HTMLButtonElement>('.btn-edit-mode-duplicate')!;
        duplicateButton.click();

        await vi.waitFor(() => expect(communityMocks.reload).toHaveBeenCalledOnce());
        expect(fetchMock).toHaveBeenNthCalledWith(1, 'http://localhost/community-playlists?target=library&page=1', expect.objectContaining({
            method: 'GET',
            headers: { 'X-CSRFToken': 'csrf-token' },
        }));
        expect(fetchMock).toHaveBeenNthCalledWith(2, '/duplicate', expect.objectContaining({
            method: 'POST',
            headers: { 'X-CSRFToken': 'csrf-token', 'Content-Type': 'application/json' },
            body: JSON.stringify({}),
        }));
        expect(communityMocks.hideModal).toHaveBeenCalledOnce();
    });
});
