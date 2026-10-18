import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import SharedSoundBoardWebSocket from '@/modules/SharedSoundBoardWebSocket';

const mocks = vi.hoisted(() => ({
    searchPlaylist: vi.fn(),
    addEventListenerDom: vi.fn(),
    initializeWarmup: vi.fn(),
    log: vi.fn(),
    error: vi.fn(),
}));

vi.mock('@/modules/General/Cookie', () => ({ default: { get: vi.fn() } }));
vi.mock('@/modules/ButtonPlaylist', () => ({
    ButtonPlaylistFinder: { search: mocks.searchPlaylist },
}));
vi.mock('@/modules/MusicElementFactory', () => ({ MusicElementFactory: {} }));
vi.mock('@/modules/UpdateVolumeElement', () => ({ default: class {} }));
vi.mock('@/modules/SoundBoardManager', () => ({ SoundBoardManager: {} }));
vi.mock('@/modules/MixerElement', () => ({ MixerElement: class {} }));
vi.mock('@/modules/UpdateVolumePlaylist', () => ({ UpdateVolumePlaylist: class {} }));
vi.mock('@/modules/General/ConsoleCustom', () => ({
    default: { log: mocks.log, error: mocks.error },
}));
vi.mock('@/modules/General/ConsoleTesteur', () => ({ default: { log: mocks.log } }));
vi.mock('@/modules/SoundBoardEventListener', () => ({
    default: class {
        addEventListenerDom = mocks.addEventListenerDom;
    },
}));
vi.mock('@/modules/StreamConnectionWarmup', () => ({
    default: class {
        initialize = mocks.initializeWarmup;
    },
}));

class FakeWebSocket {
    static current: FakeWebSocket | null = null;
    readyState = 0;
    onmessage: ((event: MessageEvent) => void) | null = null;

    constructor() {
        FakeWebSocket.current = this;
    }

    close() {
        this.readyState = 3;
    }

    send() {}
}

describe('SharedSoundBoardWebSocket', () => {
    beforeEach(() => {
        vi.stubGlobal('WebSocket', FakeWebSocket);
        vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
            ok: true,
            status: 200,
            text: vi.fn().mockResolvedValue(`
                <div id="template-shared-volume" data-shared-volume-soundboard-id="board-1">
                    <section id="refreshed-section">
                        <div id="playlist-track-1" data-id="track-1" data-last-activation="0"></div>
                    </section>
                </div>
            `),
        }));
        mocks.searchPlaylist.mockImplementation((id: string) => document.getElementById(`playlist-${id}`));
        document.body.innerHTML = `
            <div id="shared-board-refresh" data-url-refresh-board="/refresh"></div>
            <main>
                <div id="template-shared-volume" data-shared-volume-soundboard-id="board-1">
                    <section id="old-section">
                        <div id="playlist-track-1" data-id="track-1" data-last-activation="123"></div>
                    </section>
                </div>
            </main>
        `;
        SharedSoundBoardWebSocket.setNewInstance('wss://example.test', false);
    });

    afterEach(() => {
        SharedSoundBoardWebSocket.resetInstance();
        vi.unstubAllGlobals();
        vi.clearAllMocks();
        document.body.innerHTML = '';
    });

    it('replaces the existing board instead of adding a duplicate fragment', async () => {
        FakeWebSocket.current?.onmessage?.({
            data: JSON.stringify({
                type: 'reset_volume_and_hidden_board_playlist',
                data: { list_volume: {}, update_volume_after_reset: false },
            }),
        } as MessageEvent);

        await vi.waitFor(() => {
            expect(document.querySelectorAll('#template-shared-volume')).toHaveLength(1);
            expect(document.getElementById('old-section')).toBeNull();
        });

        expect(document.getElementById('refreshed-section')).not.toBeNull();
        expect(document.getElementById('playlist-track-1')?.dataset.lastActivation).toBe('123');
        expect(document.getElementById('shared-board-refresh')?.innerHTML).toBe('');
        expect(mocks.addEventListenerDom).toHaveBeenCalledOnce();
        expect(mocks.initializeWarmup).toHaveBeenCalledOnce();
    });
});
