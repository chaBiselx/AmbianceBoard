import { beforeEach, describe, expect, it, vi } from 'vitest';
import { PlayerCustom, PlayerCustomFactory } from '@/modules/Audio/PlayerCustom';

const playerMocks = vi.hoisted(() => ({ notify: vi.fn() }));
vi.mock('@/modules/General/Notifications', () => ({ default: { createClientNotification: playerMocks.notify } }));

const createPlayer = (duration = 125.6) => {
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
    container.appendChild(audio);
    document.body.appendChild(container);
    const player = new PlayerCustom(container);
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
});