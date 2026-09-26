import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import SoundboardEditMode from '@/modules/SoundBoardEditor/SoundboardEditMode';

const editMocks = vi.hoisted(() => ({
    csrf: vi.fn(),
    notify: vi.fn(),
    showModal: vi.fn(),
    hideModal: vi.fn(),
    popupShow: vi.fn(),
    bindPlaylists: vi.fn(),
    initializeMixer: vi.fn(),
    updateWidths: vi.fn(),
}));

vi.mock('@/modules/General/Csrf', () => ({ default: { getToken: editMocks.csrf } }));
vi.mock('@/modules/General/Notifications', () => ({ default: { createClientNotification: editMocks.notify } }));
vi.mock('@/modules/General/Modal', () => ({
    default: {
        show: editMocks.showModal,
        getInstance: () => ({ hide: editMocks.hideModal }),
    },
}));
vi.mock('@/modules/SoundBoardEditor/PopupAddMusicToSoundboard', () => ({
    default: class {
        showIfValue() {
            editMocks.popupShow();
        }
    },
}));
vi.mock('@/modules/SoundBoardEventListener', () => ({
    default: class {
        addEventListenerDom() {
            editMocks.bindPlaylists();
        }
    },
}));
vi.mock('@/modules/MixerManager', () => ({
    MixerManager: class {
        initializeEventListeners() {
            editMocks.initializeMixer();
        }

        static updatePlaylistVolumeWidths() {
            editMocks.updateWidths();
        }
    },
}));

const listMarkup = `
    <div id="pagination">
        <li class="page-item"><button class="page-link" data-page="2">2</button></li>
    </div>
    <form>
        <select name="genre" data-edit-mode-filter="true">
            <option value="">All</option><option value="ambient">Ambient</option>
        </select>
    </form>
    <button class="btn-edit-mode-duplicate" data-url-duplication="/duplicate">Duplicate</button>
`;

describe('SoundboardEditMode AJAX workflow', () => {
    beforeEach(() => {
        vi.clearAllMocks();
        editMocks.csrf.mockReturnValue('csrf-token');
        document.body.innerHTML = `
            <section class="responsive-sections-container" data-soundboard-editable="true">
                <div class="flex-container">
                    <a class="playlist-link">Existing playlist</a>
                    <button class="soundboard-edit-add-zone" data-soundboard-edit-open-panel="true" data-section="3">Add</button>
                </div>
            </section>
            <button id="btn-soundboard-edit-mode" data-url-panel="/panel"></button>
            <div class="soundboard-menu-edition"></div>
            <button id="soundboard-add-section-button" class="d-none"></button>
        `;
        editMocks.showModal.mockImplementation((options: { body: string }) => {
            document.body.insertAdjacentHTML('beforeend', options.body);
        });
    });

    afterEach(() => {
        vi.unstubAllGlobals();
    });

    it('loads and filters both lists, creates a playlist, and duplicates an existing one', async () => {
        const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
            const url = String(input);
            const requestUrl = new URL(url, globalThis.location.origin);
            if (url === '/panel') {
                return { text: async () => `
                    <form id="soundboard-edit-mode-create-form" data-url-create="/create">
                        <input name="name" value="New playlist">
                        <button id="soundboard-edit-mode-create-submit" type="submit">Create</button>
                    </form>
                    <div id="soundboard-edit-playlist-list-container" data-url-list="/playlists"></div>
                    <div id="soundboard-edit-my-playlist-list-container" data-url-list="/my-playlists"></div>
                ` } as Response;
            }
            if (requestUrl.pathname === '/playlists' || requestUrl.pathname === '/my-playlists') {
                if (requestUrl.pathname === '/my-playlists') {
                    return { text: async () => '<button class="btn-edit-mode-add-my-playlist" data-url-add="/add-my-playlist">Add</button>' } as Response;
                }
                return { text: async () => listMarkup } as Response;
            }
            if (url === '/add-my-playlist') {
                return {
                    ok: true,
                    json: async () => ({ success: true, message: 'Added', playlist_html: '<a class="playlist-link">Added</a>' }),
                } as Response;
            }
            if (url === '/create') {
                return {
                    ok: true,
                    json: async () => ({ success: true, message: 'Created', playlist_html: '<a class="playlist-link">Created</a>', add_music_url: '/add-music' }),
                } as Response;
            }
            if (url === '/duplicate') {
                return {
                    ok: true,
                    json: async () => ({ success: true, message: 'Duplicated', playlist_html: '<a class="playlist-link">Duplicated</a>', add_music_url: '/add-music' }),
                } as Response;
            }
            throw new Error(`Unexpected request ${init?.method} ${url}`);
        });
        vi.stubGlobal('fetch', fetchMock);

        const editMode = new SoundboardEditMode();
        editMode.addEvent();
        document.getElementById('btn-soundboard-edit-mode')!.click();
        document.querySelector<HTMLButtonElement>('.soundboard-edit-add-zone')!.click();

        await vi.waitFor(() => expect(editMocks.showModal).toHaveBeenCalledOnce());
        expect(fetchMock).toHaveBeenCalledWith('/panel', expect.objectContaining({ method: 'GET' }));
        const modalOptions = editMocks.showModal.mock.calls[0][0] as { callback: () => void };
        modalOptions.callback();

        await vi.waitFor(() => expect(document.querySelector('.btn-edit-mode-duplicate')).not.toBeNull());
        expect(document.querySelector('.btn-edit-mode-add-my-playlist')).not.toBeNull();

        const filter = document.querySelector<HTMLSelectElement>('#soundboard-edit-playlist-list-container select')!;
        filter.value = 'ambient';
        filter.dispatchEvent(new Event('change'));
        await vi.waitFor(() => expect(fetchMock.mock.calls.some(([url]) =>
            new URL(String(url), globalThis.location.origin).pathname === '/playlists' &&
            new URL(String(url), globalThis.location.origin).search === '?page=1&genre=ambient'
        )).toBe(true));

        document.querySelector<HTMLButtonElement>('#soundboard-edit-playlist-list-container .page-link')!.click();
        await vi.waitFor(() => expect(fetchMock.mock.calls.some(([url]) =>
            new URL(String(url), globalThis.location.origin).pathname === '/playlists' &&
            new URL(String(url), globalThis.location.origin).search === '?page=2&genre=ambient'
        )).toBe(true));

        document.querySelector<HTMLButtonElement>('.btn-edit-mode-add-my-playlist')!.click();
        await vi.waitFor(() => expect(editMocks.notify).toHaveBeenCalledWith({ message: 'Added', type: 'success' }));
        expect(document.querySelector('.flex-container .playlist-link:last-of-type')?.textContent).toBe('Added');

        const createForm = document.getElementById('soundboard-edit-mode-create-form') as HTMLFormElement;
        createForm.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }));
        await vi.waitFor(() => expect(editMocks.notify).toHaveBeenCalledWith({ message: 'Created', type: 'success' }));
        await vi.waitFor(() => expect(editMocks.popupShow).toHaveBeenCalledOnce());
        expect(editMocks.hideModal).toHaveBeenCalledTimes(2);
        expect(document.querySelector('.flex-container .playlist-link:last-of-type')?.textContent).toBe('Created');

        const duplicate = document.querySelector<HTMLButtonElement>('#soundboard-edit-playlist-list-container .btn-edit-mode-duplicate')!;
        duplicate.click();
        await vi.waitFor(() => expect(editMocks.notify).toHaveBeenCalledWith({ message: 'Duplicated', type: 'success' }));
        expect(duplicate.disabled).toBe(true);
        expect(editMocks.bindPlaylists).toHaveBeenCalled();
        expect(editMocks.initializeMixer).toHaveBeenCalled();
        expect(editMocks.updateWidths).toHaveBeenCalled();
    });
});