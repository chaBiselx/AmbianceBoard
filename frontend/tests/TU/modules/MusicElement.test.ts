import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { MusicElement } from '@/modules/MusicElement';
import Config from '@/modules/General/Config';
import type { MusicElementDTO } from '@/modules/MusicElementFactory';
import type { IAudioAdapter } from '@/modules/Audio/IAudioAdapter';

const musicMocks = vi.hoisted(() => ({
    cookieGet: vi.fn(),
    searchPlaylist: vi.fn(),
    selectFade: vi.fn(),
    fadeDuration: vi.fn(),
    fadeStart: vi.fn(),
    fadeSkip: vi.fn(),
    fadeCompletion: null as null | (() => void),
    createPlaylistLink: vi.fn(),
    sendMessage: vi.fn(),
    isSlavePage: vi.fn(),
    emit: vi.fn(),
    notify: vi.fn(),
    traceError: vi.fn(),
    log: vi.fn(),
    info: vi.fn(),
}));

vi.mock('@/modules/General/Cookie', () => ({ default: { get: musicMocks.cookieGet } }));
vi.mock('@/modules/ButtonPlaylist', () => ({ ButtonPlaylistFinder: { search: musicMocks.searchPlaylist } }));
vi.mock('@/modules/SharedSoundBoardUtil', () => ({ default: { isSlavePage: musicMocks.isSlavePage } }));
vi.mock('@/modules/SharedSoundBoardWebSocket', () => ({
    default: { getMasterInstance: () => ({ sendMessage: musicMocks.sendMessage }) },
}));
vi.mock('@/modules/SoundBoardManager', () => ({ SoundBoardManager: { createPlaylistLink: musicMocks.createPlaylistLink } }));
vi.mock('@/modules/FadeStartegy', () => ({
    default: {
        FadeSelector: { selectTypeFade: musicMocks.selectFade },
        LinearFade: class {},
    },
}));
vi.mock('@/modules/AudioFadeManager', () => ({
    default: class {
        constructor(_element: unknown, _strategy: unknown, _fadeIn: boolean, onComplete: (() => void) | null) {
            musicMocks.fadeCompletion = onComplete;
        }

        setDuration(duration: number) {
            musicMocks.fadeDuration(duration);
        }

        start() {
            musicMocks.fadeStart();
        }

        skip() {
            musicMocks.fadeSkip();
            musicMocks.fadeCompletion?.();
        }
    },
}));
vi.mock('@/modules/General/Notifications', () => ({ default: { createClientNotification: musicMocks.notify } }));
vi.mock('@/modules/General/ConsoleTraceServeur', () => ({ default: { error: musicMocks.traceError } }));
vi.mock('@/modules/General/ConsoleCustom', () => ({ default: { log: musicMocks.log } }));
vi.mock('@/modules/General/ConsoleTesteur', () => ({
    default: { log: musicMocks.log, info: musicMocks.info },
}));
vi.mock('@/modules/Script/SoundEventBus', () => ({ default: { emit: musicMocks.emit } }));

type AudioListener = (event: Event) => void;

const createAudioAdapter = () => {
    const listeners = new Map<string, AudioListener[]>();
    const adapter: IAudioAdapter = {
        getSource: vi.fn(() => '/audio/current'),
        setSource: vi.fn(),
        setDatasetValue: vi.fn(),
        getDatasetValue: vi.fn(),
        setPreload: vi.fn(),
        setControls: vi.fn(),
        setClassName: vi.fn(),
        addClass: vi.fn(),
        getCurrentTime: vi.fn(() => 98),
        setCurrentTime: vi.fn(),
        getDuration: vi.fn(() => 100),
        getReadyState: vi.fn(() => 2),
        setVolume: vi.fn(),
        addEventListener: vi.fn((type, listener) => {
            const callback = listener as AudioListener;
            listeners.set(type, [...(listeners.get(type) ?? []), callback]);
        }),
        removeEventListener: vi.fn(),
        appendTo: vi.fn(),
        remove: vi.fn(),
        play: vi.fn().mockResolvedValue(undefined),
        getError: vi.fn(() => null),
    };
    return {
        adapter,
        trigger: (type: string) => (listeners.get(type) ?? []).forEach(listener => listener(new Event(type))),
    };
};

const createDto = (overrides: Partial<MusicElementDTO> = {}): MusicElementDTO => ({
    butonPlaylistToken: 'token-1',
    defaultVolume: 0.8,
    fadeIn: false,
    fadeInType: 'disabled',
    fadeInDuration: 0,
    fadeOut: false,
    fadeOutType: 'linear',
    fadeOutDuration: 2,
    playlistType: 'music',
    idPlaylist: 'playlist-1',
    playlistLoop: false,
    delay: 0,
    baseUrl: '/audio/current',
    durationRemainingTriggerNextMusic: 0,
    fadeOffOnStop: false,
    fadeOffOnStopDuration: 0,
    fadeOffOnStopType: 'disabled',
    ...overrides,
});

describe('MusicElement', () => {
    beforeEach(() => {
        vi.clearAllMocks();
        vi.useFakeTimers();
        musicMocks.cookieGet.mockReturnValue(null);
        musicMocks.isSlavePage.mockReturnValue(false);
        musicMocks.searchPlaylist.mockReturnValue({
            isActive: () => true,
            disactive: vi.fn(),
            isActivePlaylist: true,
            getToken: () => 'token-1',
        });
        document.body.innerHTML = `<div id="${Config.SOUNDBOARD_DIV_ID_PLAYERS}"></div>`;
    });

    afterEach(() => {
        vi.useRealTimers();
    });

    it('initializes from its DTO and delegates audio element operations to the adapter', () => {
        const { adapter } = createAudioAdapter();
        const element = new MusicElement(adapter, createDto());

        element.setDefaultVolume(0.4);
        element.setSpecificMusic('/audio/specific');
        element.setVolume(0.3);
        element.addToDOM();

        expect(element.idPlaylist).toBe('playlist-1');
        expect(element.defaultVolume).toBe(0.4);
        expect(adapter.setDatasetValue).toHaveBeenCalledWith('defaultvolume', '0.4');
        expect(adapter.setDatasetValue).toHaveBeenCalledWith('baseurl', '/audio/specific');
        expect(adapter.setSource).toHaveBeenCalledWith('/audio/specific');
        expect(adapter.setVolume).toHaveBeenCalledWith(0.3);
        expect(adapter.appendTo).toHaveBeenCalledWith(document.getElementById(Config.SOUNDBOARD_DIV_ID_PLAYERS));
        expect(adapter.setPreload).toHaveBeenCalledWith('metadata');
    });

    it('removes audio without playing when its playlist is inactive', () => {
        const { adapter } = createAudioAdapter();
        musicMocks.searchPlaylist.mockReturnValue({ isActive: () => false });
        new MusicElement(adapter, createDto()).play();

        expect(adapter.remove).toHaveBeenCalledOnce();
        expect(adapter.play).not.toHaveBeenCalled();
    });

    it('plays active playlists and cleans up after the ended event', () => {
        const { adapter, trigger } = createAudioAdapter();
        const element = new MusicElement(adapter, createDto());
        element.play();

        expect(adapter.play).toHaveBeenCalledOnce();
        trigger('ended');
        vi.advanceTimersByTime(35);

        expect(adapter.remove).toHaveBeenCalledOnce();
        expect(musicMocks.emit).toHaveBeenCalledWith('music:ended', { playlistId: 'playlist-1', token: 'token-1' });
    });

    it('starts a fade-out at the configured remaining-time threshold and schedules the next loop', () => {
        const { adapter, trigger } = createAudioAdapter();
        const button = { isActive: () => true, getToken: () => 'token-1' };
        musicMocks.searchPlaylist.mockReturnValue(button);
        const element = new MusicElement(adapter, createDto({
            durationRemainingTriggerNextMusic: 5,
            playlistLoop: true,
        }));
        element.play();
        trigger('loadedmetadata');
        trigger('timeupdate');

        expect(musicMocks.fadeStart).toHaveBeenCalledOnce();
        expect(musicMocks.createPlaylistLink).toHaveBeenCalledWith(button);
        expect(adapter.removeEventListener).toHaveBeenCalledWith('timeupdate', expect.any(Function));
    });

    it('defers fade-out for short tracks until the ended event', () => {
        const { adapter, trigger } = createAudioAdapter();
        adapter.getDuration = vi.fn(() => 6);
        const element = new MusicElement(adapter, createDto({
            durationRemainingTriggerNextMusic: 5,
            fadeOutDuration: 2,
            playlistLoop: true,
        }));
        element.play();
        trigger('loadedmetadata');
        trigger('timeupdate');

        expect(musicMocks.fadeStart).not.toHaveBeenCalled();
        trigger('ended');
        vi.advanceTimersByTime(35);

        expect(adapter.remove).toHaveBeenCalledOnce();
        expect(musicMocks.createPlaylistLink).toHaveBeenCalledOnce();
    });

    it('skips a fade-in that is longer than the track and signals a 404 audio error', () => {
        const { adapter, trigger } = createAudioAdapter();
        adapter.getDuration = vi.fn(() => 2);
        musicMocks.searchPlaylist.mockReturnValue({ isActive: () => true, disactive: vi.fn() });
        const element = new MusicElement(adapter, createDto({ fadeInType: 'linear', fadeInDuration: 2 }));
        element.play();
        trigger('playing');

        expect(musicMocks.fadeSkip).toHaveBeenCalledOnce();
        expect(element.fadeInGoing).toBe(false);

        adapter.getError = vi.fn(() => ({ code: 4, message: 'not found' } as MediaError));
        trigger('error');
        expect(musicMocks.traceError).toHaveBeenCalledOnce();
        expect(musicMocks.notify).toHaveBeenCalledWith(expect.objectContaining({ type: 'danger' }));
        expect(adapter.remove).toHaveBeenCalledOnce();
    });

    it('stops immediately when configured and notifies the shared master', () => {
        musicMocks.cookieGet.mockReturnValue('websocket-token');
        const { adapter } = createAudioAdapter();
        const button = { disactive: vi.fn() };
        musicMocks.searchPlaylist.mockReturnValue(button);
        const element = new MusicElement(adapter, createDto());
        element.WebSocketActive = true;

        element.delete();

        expect(button.disactive).toHaveBeenCalledOnce();
        expect(adapter.remove).toHaveBeenCalledOnce();
        expect(musicMocks.sendMessage).toHaveBeenCalledWith({
            type: 'music_stop',
            track: null,
            playlist_uuid: 'playlist-1',
        });
        expect(musicMocks.emit).toHaveBeenCalledWith('music:stopped', { playlistId: 'playlist-1', token: 'token-1' });
    });
});