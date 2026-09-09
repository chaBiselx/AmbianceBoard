import { beforeEach, describe, expect, it, vi } from 'vitest';

vi.mock('@/modules/ButtonPlaylist', () => ({
    ButtonPlaylistFinder: { search: vi.fn() }
}));
vi.mock('@/modules/SoundBoardManager', () => ({
    SoundBoardManager: { addPlaylist: vi.fn(), removePlaylist: vi.fn() }
}));
vi.mock('@/modules/UpdateVolumePlaylist', () => ({
    UpdateVolumePlaylist: vi.fn().mockImplementation(() => ({ updateVolume: vi.fn() }))
}));

import { ButtonPlaylistFinder } from '@/modules/ButtonPlaylist';
import { SoundBoardManager } from '@/modules/SoundBoardManager';
import ScriptRunner from '@/modules/Script/ScriptRunner';
import SoundEventBus from '@/modules/Script/SoundEventBus';
import { ScriptDTO, ScriptStepDTO } from '@/modules/Script/ScriptTypes';

const PLAYLIST_A = 'playlist-a';
const PLAYLIST_B = 'playlist-b';

const buildStep = (overrides: Partial<ScriptStepDTO> & { uuid: string }): ScriptStepDTO => ({
    order: 0,
    action_type: 'PLAY_PLAYLIST',
    trigger_type: 'IMMEDIATE',
    trigger_offset_ms: 0,
    trigger_source_step_uuid: null,
    params: { playlist_uuid: PLAYLIST_A },
    ...overrides,
});

const buildScript = (steps: ScriptStepDTO[]): ScriptDTO => ({
    uuid: 'script-1',
    name: 'Intro',
    color: '#000000',
    colorText: '#ffffff',
    order: 0,
    enabled: true,
    steps,
});

const buildButton = (active = false) => {
    let isActive = active;
    return {
        isActive: () => isActive,
        active: vi.fn(() => { isActive = true; }),
        disactive: vi.fn(() => { isActive = false; }),
    };
};

describe('ScriptRunner', () => {
    beforeEach(() => {
        vi.clearAllMocks();
        vi.useFakeTimers();
        SoundEventBus.reset();
        (ButtonPlaylistFinder.search as ReturnType<typeof vi.fn>).mockImplementation(() => buildButton());
    });

    it('plays an immediate step as soon as the script starts', () => {
        const runner = new ScriptRunner(buildScript([buildStep({ uuid: 'step-1' })]));

        runner.start();
        vi.advanceTimersByTime(0);

        expect(SoundBoardManager.addPlaylist).toHaveBeenCalledTimes(1);
    });

    it('delays a timecode step until its offset is reached', () => {
        const runner = new ScriptRunner(buildScript([
            buildStep({ uuid: 'step-1', trigger_type: 'TIMECODE', trigger_offset_ms: 5000 }),
        ]));

        runner.start();
        vi.advanceTimersByTime(4999);
        expect(SoundBoardManager.addPlaylist).not.toHaveBeenCalled();

        vi.advanceTimersByTime(1);
        expect(SoundBoardManager.addPlaylist).toHaveBeenCalledTimes(1);
    });

    it('chains a step on the end of a previous one', () => {
        const runner = new ScriptRunner(buildScript([
            buildStep({ uuid: 'step-1' }),
            buildStep({
                uuid: 'step-2',
                trigger_type: 'ON_STEP_END',
                trigger_source_step_uuid: 'step-1',
                trigger_offset_ms: 1000,
                params: { playlist_uuid: PLAYLIST_B },
            }),
        ]));

        runner.start();
        vi.advanceTimersByTime(0);
        expect(SoundBoardManager.addPlaylist).toHaveBeenCalledTimes(1);

        SoundEventBus.emit('music:ended', { playlistId: PLAYLIST_A, token: null });
        vi.advanceTimersByTime(999);
        expect(SoundBoardManager.addPlaylist).toHaveBeenCalledTimes(1);

        vi.advanceTimersByTime(1);
        expect(SoundBoardManager.addPlaylist).toHaveBeenCalledTimes(2);
    });

    it('ignores the end of an unrelated playlist', () => {
        const runner = new ScriptRunner(buildScript([
            buildStep({ uuid: 'step-1' }),
            buildStep({
                uuid: 'step-2',
                trigger_type: 'ON_STEP_END',
                trigger_source_step_uuid: 'step-1',
                params: { playlist_uuid: PLAYLIST_B },
            }),
        ]));

        runner.start();
        vi.advanceTimersByTime(0);

        SoundEventBus.emit('music:ended', { playlistId: 'other-playlist', token: null });
        vi.advanceTimersByTime(1000);

        expect(SoundBoardManager.addPlaylist).toHaveBeenCalledTimes(1);
    });

    it('cancels pending steps and stops started playlists when stopped', () => {
        const button = buildButton();
        (ButtonPlaylistFinder.search as ReturnType<typeof vi.fn>).mockReturnValue(button);

        const runner = new ScriptRunner(buildScript([
            buildStep({ uuid: 'step-1' }),
            buildStep({ uuid: 'step-2', trigger_type: 'TIMECODE', trigger_offset_ms: 5000 }),
        ]));

        runner.start();
        vi.advanceTimersByTime(0);
        runner.stop();
        vi.advanceTimersByTime(10000);

        expect(SoundBoardManager.addPlaylist).toHaveBeenCalledTimes(1);
        expect(SoundBoardManager.removePlaylist).toHaveBeenCalledTimes(1);
        expect(runner.isRunning()).toBe(false);
    });

    it('notifies completion once every step has run', () => {
        const onFinished = vi.fn();
        const runner = new ScriptRunner(buildScript([buildStep({ uuid: 'step-1', action_type: 'STOP_PLAYLIST' })]), onFinished);

        runner.start();
        vi.advanceTimersByTime(0);

        expect(onFinished).toHaveBeenCalledTimes(1);
        expect(runner.isRunning()).toBe(false);
    });

    it('keeps running the rest of the script when an action is unknown', () => {
        const runner = new ScriptRunner(buildScript([
            buildStep({ uuid: 'step-1', action_type: 'DOES_NOT_EXIST' }),
            buildStep({ uuid: 'step-2' }),
        ]));

        runner.start();
        vi.advanceTimersByTime(0);

        expect(SoundBoardManager.addPlaylist).toHaveBeenCalledTimes(1);
    });
});
