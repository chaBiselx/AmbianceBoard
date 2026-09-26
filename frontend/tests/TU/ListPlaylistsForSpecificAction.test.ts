import { beforeEach, describe, expect, it, vi } from 'vitest';

const playlistActionMocks = vi.hoisted(() => ({
    csrf: vi.fn(),
    debug: vi.fn(),
    error: vi.fn(),
    notify: vi.fn(),
    detectKeyboard: vi.fn(),
    setupFocus: vi.fn(),
    onShortcut: null as null | ((shortcut: string[]) => boolean),
    onCancel: null as null | ((cancel: boolean) => void),
    stopListening: vi.fn(),
}));

vi.mock('@/modules/General/PageFocusReloader', () => ({ default: class { setupFocusListener() { playlistActionMocks.setupFocus(); } } }));
vi.mock('@/modules/General/Csrf', () => ({ default: { getToken: playlistActionMocks.csrf } }));
vi.mock('@/modules/General/ConsoleCustom', () => ({
    default: { debug: playlistActionMocks.debug, error: playlistActionMocks.error },
}));
vi.mock('@/modules/Control/ShorcutKeyBoardDetector', () => ({
    default: class {
        startListening(onShortcut: (shortcut: string[]) => boolean, onCancel: (cancel: boolean) => void) {
            playlistActionMocks.onShortcut = onShortcut;
            playlistActionMocks.onCancel = onCancel;
        }
        stopListening() { playlistActionMocks.stopListening(); }
    },
}));
vi.mock('@/modules/Util/UserConfig', () => ({ default: { detectKeyboard: playlistActionMocks.detectKeyboard } }));
vi.mock('@/modules/General/Notifications', () => ({ default: { createClientNotification: playlistActionMocks.notify } }));

describe('ListPlaylistsForSpecificAction page script', () => {
    beforeEach(() => {
        vi.resetModules();
        vi.clearAllMocks();
        playlistActionMocks.csrf.mockReturnValue('csrf-token');
        playlistActionMocks.detectKeyboard.mockReturnValue(false);
        playlistActionMocks.onShortcut = null;
        playlistActionMocks.onCancel = null;
        document.body.innerHTML = `
            <div id="col-actionnable-by-players" data-actionnable-by-players-url="/actionable"></div>
            <div id="col-keyboard-shortcut" data-shortcut-url="/shortcuts"></div>
            <div class="keyboard-shortcut-column"></div>
            <div id="playlists-table-body">
                <input class="update-action" type="checkbox" data-playlist-uuid="playlist-1"
                    data-soundboard-uuid="board-1" data-soundboard-playlist-id="42" data-label="Ambient">
                <button class="keyboard-shortcut-event" data-playlist-uuid="playlist-1"
                    data-soundboard-uuid="board-1" data-soundboard-playlist-id="42"
                    data-value-default="Alt + Q" data-name="Ambient">Alt + Q</button>
                <button class="keyboard-shortcut-event" data-playlist-uuid="playlist-2"
                    data-soundboard-uuid="board-1" data-soundboard-playlist-id="43"
                    data-value-default="Shift + Y" data-name="Other">Shift + Y</button>
            </div>
        `;
    });

    it('saves actionable values and applies, rejects duplicates, and clears shortcuts', async () => {
        const fetchMock = vi.fn().mockResolvedValue({ status: 200 });
        vi.stubGlobal('fetch', fetchMock);
        await import('@/ListPlaylistsForSpecificAction');
        document.dispatchEvent(new Event('DOMContentLoaded'));

        expect(playlistActionMocks.setupFocus).toHaveBeenCalledOnce();
        expect(document.querySelector<HTMLElement>('.keyboard-shortcut-column')!.style.display).toBe('none');
        const actionable = document.querySelector<HTMLInputElement>('.update-action')!;
        actionable.click();
        await vi.waitFor(() => expect(playlistActionMocks.debug).toHaveBeenCalledWith('Valeur mise a jour'));
        expect(fetchMock).toHaveBeenCalledWith('/actionable', expect.objectContaining({
            method: 'UPDATE',
            body: JSON.stringify({
                soundboard_uuid: 'board-1',
                playlist_uuid: 'playlist-1',
                soundboard_playlist_id: '42',
                label: 'Ambient',
                value: true,
            }),
        }));

        const shortcutButton = document.querySelector<HTMLButtonElement>('.keyboard-shortcut-event')!;
        shortcutButton.click();
        playlistActionMocks.onShortcut!(['Ctrl', 'X']);
        await vi.waitFor(() => expect(fetchMock).toHaveBeenCalledWith('/shortcuts', expect.objectContaining({
            method: 'UPDATE',
            body: JSON.stringify({
                soundboard_uuid: 'board-1',
                playlist_uuid: 'playlist-1',
                soundboard_playlist_id: '42',
                shortcuts: ['Ctrl', 'X'],
            }),
        })));
        expect(shortcutButton.textContent).toBe('Ctrl + X');

        document.querySelector<HTMLButtonElement>('[data-playlist-uuid="playlist-2"]')!.dataset.valueDefault = 'Ctrl + X';
        shortcutButton.click();
        playlistActionMocks.onShortcut!(['Ctrl', 'X']);
        expect(playlistActionMocks.notify).toHaveBeenCalledWith(expect.objectContaining({
            message: expect.stringContaining('Le raccourci clavier Ctrl + X existe déjà'),
            type: 'info',
        }));
        expect(shortcutButton.textContent).toBe('Ctrl + X');

        const clearFetch = vi.fn().mockRejectedValue(new Error('offline'));
        vi.stubGlobal('fetch', clearFetch);
        shortcutButton.click();
        playlistActionMocks.onCancel!(false);
        await vi.waitFor(() => expect(playlistActionMocks.notify).toHaveBeenCalledWith({
            message: 'Une erreur est survenue',
            type: 'error',
        }));
        expect(shortcutButton.textContent).toBe('-');
        expect(playlistActionMocks.stopListening).toHaveBeenCalled();
    });
});