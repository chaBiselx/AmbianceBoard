import { beforeEach, describe, expect, it, vi } from 'vitest';
import { PlayerCustom, PlayerCustomFactory } from '@/modules/Audio/PlayerCustom';

const playerMocks = vi.hoisted(() => ({ notify: vi.fn() }));
vi.mock('@/modules/General/Notifications', () => ({ default: { createClientNotification: playerMocks.notify } }));

const createPlayer = (duration = 125.6, onPlay?: (player: PlayerCustom) => void) => {
    const container = document.createElement('div');
    container.className = 'player-custom';
    container.dataset.url = '/audio/preview.mp3';
    const audio = document.createElement('audio');
    let paused = true;
    let currentTime = 0;
    Object.defineProperties(audio, {
        paused: { configurable: true, get: () => paused },
        duration: { configurable: true, get: () => duration },
        currentTime: {
            configurable: true,
            get: () => currentTime,
            set: (value: number) => { currentTime = value; },
        },
    });
    audio.play = vi.fn(() => {
        paused = false;
        return Promise.resolve();
    });
    audio.pause = vi.fn(() => { paused = true; });
    audio.load = vi.fn();
    container.appendChild(audio);
    document.body.appendChild(container);
    const player = new PlayerCustom(container, onPlay);
    player.generate();
    return { container, audio, player };
};

describe('PlayerCustom', () => {
    beforeEach(() => {
        vi.clearAllMocks();
        document.body.innerHTML = '';
    });

    it('generates controls, loads audio lazily, updates timing, seeks, pauses, and reloads', () => {
        const { container, audio, player } = createPlayer();
        const playButton = container.querySelector<HTMLButtonElement>('.btn-play')!;
        const reloadButton = container.querySelector<HTMLButtonElement>('.btn-reload')!;
        const seeker = container.querySelector<HTMLInputElement>('.seeker-input')!;

        expect(container.querySelector('.player-custom-container')).not.toBeNull();
        expect(seeker.disabled).toBe(true);
        playButton.click();

        expect(audio.src).toContain('/audio/preview.mp3');
        expect(audio.play).toHaveBeenCalledOnce();
        expect(seeker.disabled).toBe(false);
        expect(container.querySelector('.seeker')!.classList.contains('d-block')).toBe(true);
        expect(container.querySelector('.timer')!.classList.contains('d-inline-block')).toBe(true);
        expect(container.querySelector('.play-icon')!.classList.contains('d-none')).toBe(true);

        audio.dispatchEvent(new Event('loadedmetadata'));
        expect(container.querySelector('.duration')!.textContent).toBe('2:05');
        audio.currentTime = 61;
        audio.dispatchEvent(new Event('timeupdate'));
        expect(container.querySelector('.current-time')!.textContent).toBe('1:01');
        expect(Number(seeker.value)).toBeCloseTo(61 / 125.6 * 100, 0);

        seeker.value = '50';
        seeker.dispatchEvent(new Event('input'));
        expect(audio.currentTime).toBeCloseTo(62.8);

        playButton.click();
        expect(audio.pause).toHaveBeenCalledOnce();
        expect(container.querySelector('.play-icon')!.classList.contains('d-none')).toBe(false);

        reloadButton.click();
        expect(audio.currentTime).toBe(0);
        expect(audio.play).toHaveBeenCalledTimes(2);

        audio.dispatchEvent(new Event('error'));
        expect(playerMocks.notify).toHaveBeenCalledWith({
            message: "Erreur lors de la lecture de l'audio.",
            type: 'danger',
            duration: 2000,
        });
        expect(player.instanceLoaded).toBe(true);
    });

    it('formats an infinite media duration and creates a player for each matching element', () => {
        const first = createPlayer(Number.POSITIVE_INFINITY);
        first.player.togglePlayer();
        first.audio.dispatchEvent(new Event('loadedmetadata'));
        expect(first.container.querySelector('.duration')!.textContent).toBe('∞');

        const second = document.createElement('div');
        second.className = 'player-custom';
        second.dataset.url = '/audio/second.mp3';
        second.appendChild(document.createElement('audio'));
        document.body.appendChild(second);

        PlayerCustomFactory.create();

        expect(document.querySelectorAll('.player-custom-container')).toHaveLength(3);
    });

    it('coordinates play and restart only within the caller group', () => {
        const unrelated = createPlayer();
        let active: PlayerCustom | null = null;
        const coordinate = (player: PlayerCustom) => {
            if (active !== player) active?.stop(true);
            active = player;
        };
        const first = createPlayer(125, coordinate);
        const second = createPlayer(125, coordinate);
        unrelated.player.togglePlayer();
        first.player.togglePlayer();
        first.audio.currentTime = 20;
        second.player.reload();
        expect(first.audio.paused).toBe(true);
        expect(first.audio.currentTime).toBe(0);
        expect(second.audio.paused).toBe(false);
        expect(unrelated.audio.paused).toBe(false);
        first.player.togglePlayer();
        expect(second.audio.paused).toBe(true);
    });

    it('resets completed audio and removes controls, source and listeners on destroy', () => {
        const { player, audio, container } = createPlayer();
        player.generate();
        expect(container.querySelectorAll('.player-custom-container')).toHaveLength(1);
        player.togglePlayer();
        audio.currentTime = 125;
        audio.dispatchEvent(new Event('ended'));
        expect(audio.currentTime).toBe(0);
        expect(container.querySelector('.pause-icon')!.classList.contains('d-none')).toBe(true);
        const button = container.querySelector<HTMLButtonElement>('.btn-play')!;
        player.destroy();
        player.destroy();
        audio.dispatchEvent(new Event('error'));
        button.click();
        player.reload();
        expect(audio.play).toHaveBeenCalledOnce();
        expect(audio.hasAttribute('src')).toBe(false);
        expect(audio.load).toHaveBeenCalledOnce();
        expect(playerMocks.notify).not.toHaveBeenCalled();
        expect(container.querySelector('.player-custom-container')).toBeNull();
    });

    it('handles rejected play promises without leaving a playing icon', async () => {
        const { player, audio, container } = createPlayer();
        audio.play = vi.fn(() => Promise.reject(new Error('Unavailable')));
        player.togglePlayer();
        await Promise.resolve();
        expect(container.querySelector('.play-icon')!.classList.contains('d-none')).toBe(false);
        expect(playerMocks.notify).toHaveBeenCalledOnce();
    });

    it('creates players only inside the requested container', () => {
        const root = document.createElement('section');
        root.innerHTML = '<div class="player-custom" data-url="/local"><audio></audio></div>';
        document.body.appendChild(root);
        const outside = createPlayer();
        expect(PlayerCustomFactory.create(root)).toHaveLength(1);
        expect(outside.container.querySelectorAll('.player-custom-container')).toHaveLength(1);
        expect(root.querySelector('audio')!.hasAttribute('src')).toBe(false);
    });
});