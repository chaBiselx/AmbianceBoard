import { beforeEach, describe, expect, it, vi } from 'vitest';

const playerMocks = vi.hoisted(() => ({
    warmup: vi.fn(),
    soundboardEvents: vi.fn(),
    playingMonitor: vi.fn(),
    scriptManager: vi.fn(),
    mixerSetup: vi.fn(),
    mixerWidths: vi.fn(),
    mixerEvents: vi.fn(),
    wakeLock: vi.fn(),
    sharedVolume: vi.fn(),
    shortcutCallback: null as null | ((shortcut: string[]) => boolean),
    searchPlaylist: vi.fn(),
    editMode: vi.fn(),
    bindZones: vi.fn(),
    boardSections: vi.fn(),
    propose: vi.fn(),
    cookieGet: vi.fn(),
    isSlavePage: vi.fn(),
    slaveUrl: vi.fn(),
    setNewSocket: vi.fn(),
    getMasterSocket: vi.fn(),
    getSlaveSocket: vi.fn(),
    startSlaveSocket: vi.fn(),
    modalShow: vi.fn(),
    modalHide: vi.fn(),
    shareLink: vi.fn(),
    csrf: vi.fn(),
    consoleLog: vi.fn(),
    consoleError: vi.fn(),
}));

vi.mock('@/modules/General/Config', () => ({ default: { DEBUG: false, SOUNDBOARD_DIV_ID_PLAYERS: 'players' } }));
vi.mock('@/modules/General/Csrf', () => ({ default: { getToken: playerMocks.csrf } }));
vi.mock('@/modules/General/Cookie', () => ({ default: { get: playerMocks.cookieGet } }));
vi.mock('@/modules/ButtonPlaylist', () => ({ ButtonPlaylistFinder: { search: playerMocks.searchPlaylist } }));
vi.mock('@/modules/MixerManager', () => ({
    MixerManager: class {
        initializeEventListeners() { playerMocks.mixerEvents(); }
        static setUpMixerPlaylist() { playerMocks.mixerSetup(); }
        static updatePlaylistVolumeWidths() { playerMocks.mixerWidths(); }
    },
}));
vi.mock('@/modules/General/WakeLock', () => ({ default: class { start() { playerMocks.wakeLock(); } } }));
vi.mock('@/modules/General/Modal', () => ({
    default: {
        show: vi.fn((options: { body: string; callback?: () => void }) => {
            playerMocks.modalShow(options);
            document.body.insertAdjacentHTML('beforeend', options.body);
        }),
        hide: playerMocks.modalHide,
    },
}));
vi.mock('@/modules/SharedSoundBoardWebSocket', () => ({
    default: {
        setNewInstance: playerMocks.setNewSocket,
        getMasterInstance: playerMocks.getMasterSocket,
        getSlaveInstance: (url: string) => {
            playerMocks.getSlaveSocket(url);
            return { start: playerMocks.startSlaveSocket };
        },
    },
}));
vi.mock('@/modules/SharedSoundBoardUtil', () => ({
    default: { isSlavePage: playerMocks.isSlavePage, getSlaveUrl: playerMocks.slaveUrl },
}));
vi.mock('@/modules/Event/ShareLinkManager', () => ({ default: class { addEvent() { playerMocks.shareLink(); } } }));
vi.mock('@/modules/General/ConsoleTesteur', () => ({ default: { log: playerMocks.consoleLog } }));
vi.mock('@/modules/General/ConsoleCustom', () => ({
    default: { log: playerMocks.consoleLog, error: playerMocks.consoleError },
}));
vi.mock('@/modules/SharedSoundboardCustomVolume', () => ({
    SharedSoundboardCustomVolumeFactory: { create: playerMocks.sharedVolume },
}));
vi.mock('@/modules/Control/ShorcutKeyBoardDetector', () => ({
    default: class {
        startListening(callback: (shortcut: string[]) => boolean) {
            playerMocks.shortcutCallback = callback;
        }
    },
}));
vi.mock('@/modules/SoundBoardEventListener', () => ({ default: class { addEventListenerDom() { playerMocks.soundboardEvents(); } } }));
vi.mock('@/modules/StreamConnectionWarmup', () => ({ default: class { initialize() { playerMocks.warmup(); } } }));
vi.mock('@/modules/SoundBoardEditor/SoundboardEditMode', () => ({
    default: class {
        addEvent() { playerMocks.editMode(); }
        bindAddZonesIn(node: ParentNode) { playerMocks.bindZones(node); }
    },
}));
vi.mock('@/modules/SoundboardOrganizer/BoardSectionAdder', () => ({
    BoardSectionAdder: class { addEvent() { playerMocks.boardSections(); } },
}));
vi.mock('@/modules/SoundBoardEditor/ProposePlaylistToSoundboard', () => ({
    default: class { addEvent() { playerMocks.propose(); } },
}));
vi.mock('@/modules/PlayingMonitor', () => ({ default: class { init() { playerMocks.playingMonitor(); } } }));
vi.mock('@/modules/Script/ScriptManager', () => ({ default: class { init() { playerMocks.scriptManager(); } } }));

describe('SoundboardPlayer page script', () => {
    beforeEach(() => {
        vi.resetModules();
        vi.clearAllMocks();
        playerMocks.shortcutCallback = null;
        playerMocks.cookieGet.mockReturnValue(null);
        playerMocks.isSlavePage.mockReturnValue(false);
        playerMocks.sharedVolume.mockReturnValue({ addEvent: playerMocks.sharedVolume });
        playerMocks.searchPlaylist.mockReturnValue({ simulateClick: vi.fn() });
        document.body.innerHTML = `
            <div id="players"></div>
            <button id="btn-publish-soundboard" data-url="/publish"></button>
            <div id="btn-shared-playlist"></div>
            <div id="list-shortcut-keyboard"><button class="shortcut-element" data-shortcut="CTRL##M" data-playlist-uuid="playlist-1"></button></div>
        `;
    });

    it('initializes page managers, handles publishing, shortcuts, and slave playback', async () => {
        vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ text: async () => '<button class="share-link-btn"></button>' }));
        await import('@/SoundboardPlayer');
        document.dispatchEvent(new Event('DOMContentLoaded'));

        expect(playerMocks.warmup).toHaveBeenCalledOnce();
        expect(playerMocks.soundboardEvents).toHaveBeenCalledOnce();
        expect(playerMocks.playingMonitor).toHaveBeenCalledOnce();
        expect(playerMocks.scriptManager).toHaveBeenCalledOnce();
        expect(playerMocks.mixerSetup).toHaveBeenCalledOnce();
        expect(playerMocks.mixerWidths).toHaveBeenCalledOnce();
        expect(playerMocks.mixerEvents).toHaveBeenCalledOnce();
        expect(playerMocks.wakeLock).toHaveBeenCalledOnce();
        expect(playerMocks.editMode).toHaveBeenCalledOnce();
        expect(playerMocks.boardSections).toHaveBeenCalledOnce();
        expect(playerMocks.propose).toHaveBeenCalledOnce();

        const shortcutResult = playerMocks.shortcutCallback!(['CTRL', 'M']);
        expect(shortcutResult).toBe(false);
        expect(playerMocks.searchPlaylist).toHaveBeenCalledWith('playlist-1');

        document.getElementById('btn-publish-soundboard')!.click();
        await vi.waitFor(() => expect(playerMocks.shareLink).toHaveBeenCalledOnce());
        expect(playerMocks.modalShow).toHaveBeenCalledWith(expect.objectContaining({ title: 'Lien partage' }));

        playerMocks.cookieGet.mockReturnValue(btoa('wss://soundboard.example/socket'));
        document.dispatchEvent(new Event('DOMContentLoaded'));
        expect(playerMocks.setNewSocket).toHaveBeenCalledWith('wss://soundboard.example/socket', true);

        playerMocks.isSlavePage.mockReturnValue(true);
        playerMocks.slaveUrl.mockReturnValue('wss://master.example/socket');
        document.dispatchEvent(new Event('DOMContentLoaded'));
        const modal = playerMocks.modalShow.mock.calls.at(-1)![0] as { callback: () => void };
        modal.callback();
        document.getElementById('btn-start-websocket')!.click();

        expect(playerMocks.modalHide).toHaveBeenCalledOnce();
        expect(playerMocks.getSlaveSocket).toHaveBeenCalledWith('wss://master.example/socket');
        expect(playerMocks.startSlaveSocket).toHaveBeenCalledOnce();
    });
});