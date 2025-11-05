import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { MusicElementFactory, MusicElementDTO } from '@/modules/MusicElementFactory';
import { MusicElement } from '@/modules/MusicElement';
import { ButtonPlaylist } from '@/modules/ButtonPlaylist';
import Config from '@/modules/General/Config';
import SharedSoundBoardUtil from '@/modules/SharedSoundBoardUtil';
import Boolean from '@/modules/Util/Boolean';

// Mock des modules externes
vi.mock('@/modules/MusicElement');
vi.mock('@/modules/General/Config', () => ({
    default: {
        DEBUG: false,
        SOUNDBOARD_DIV_ID_PLAYERS: 'audio-players'
    }
}));
vi.mock('@/modules/SharedSoundBoardUtil', () => ({
    default: {
        isSlavePage: vi.fn(() => false)
    }
}));
vi.mock('@/modules/Util/Boolean', () => ({
    default: {
        convert: vi.fn((value) => {
            if (typeof value === 'boolean') return value;
            return value === 'true';
        })
    }
}));

describe('MusicElementFactory', () => {

    beforeEach(() => {
        vi.clearAllMocks();
    });

    describe('fromAudioElement', () => {
        let audioElement: HTMLAudioElement;

        beforeEach(() => {
            audioElement = document.createElement('audio');
            audioElement.dataset.butonPlaylistToken = 'token-123';
            audioElement.dataset.defaultvolume = '0.8';
            audioElement.dataset.fadein = 'true';
            audioElement.dataset.fadeintype = 'exponential';
            audioElement.dataset.fadeinduration = '2.5';
            audioElement.dataset.fadeout = 'true';
            audioElement.dataset.fadeouttype = 'logarithmic';
            audioElement.dataset.fadeoutduration = '3.0';
            audioElement.dataset.playlisttype = 'music';
            audioElement.dataset.playlistid = 'playlist-456';
            audioElement.dataset.playlistloop = 'true';
            audioElement.dataset.playlistdelay = '5.0';
            audioElement.dataset.baseurl = 'https://example.com/music.mp3';
            audioElement.dataset.durationremainingtriggernextmusic = '10.0';
        });

        it('should create a MusicElement from an HTMLAudioElement with all properties', () => {
            MusicElementFactory.fromAudioElement(audioElement);

            expect(MusicElement).toHaveBeenCalledWith(
                audioElement,
                expect.objectContaining({
                    butonPlaylistToken: 'token-123',
                    defaultVolume: 0.8,
                    fadeIn: true,
                    fadeInType: 'exponential',
                    fadeInDuration: 2.5,
                    fadeOut: true,
                    fadeOutType: 'logarithmic',
                    fadeOutDuration: 3,
                    playlistType: 'music',
                    idPlaylist: 'playlist-456',
                    playlistLoop: true,
                    delay: 5,
                    baseUrl: 'https://example.com/music.mp3',
                    durationRemainingTriggerNextMusic: 10
                })
            );
        });

        it('should handle missing optional properties with defaults', () => {
            const minimalAudio = document.createElement('audio');
            
            MusicElementFactory.fromAudioElement(minimalAudio);

            expect(MusicElement).toHaveBeenCalledWith(
                minimalAudio,
                expect.objectContaining({
                    butonPlaylistToken: null,
                    defaultVolume: 1,
                    fadeIn: false,
                    fadeInType: 'linear',
                    fadeInDuration: 0,
                    fadeOut: false,
                    fadeOutType: 'linear',
                    fadeOutDuration: 0,
                    playlistType: '',
                    idPlaylist: '',
                    playlistLoop: false,
                    delay: 0,
                    baseUrl: '',
                    durationRemainingTriggerNextMusic: 0
                })
            );
        });

        it('should parse boolean values correctly', () => {
            audioElement.dataset.fadein = 'true';
            audioElement.dataset.fadeout = 'false';
            audioElement.dataset.playlistloop = 'true';

            MusicElementFactory.fromAudioElement(audioElement);

            const calledDTO = (MusicElement as any).mock.calls[0][1] as MusicElementDTO;
            expect(calledDTO.fadeIn).toBe(true);
            expect(calledDTO.fadeOut).toBe(false);
            expect(calledDTO.playlistLoop).toBe(true);
        });

        it('should parse numeric values correctly', () => {
            audioElement.dataset.defaultvolume = '0.65';
            audioElement.dataset.fadeinduration = '1.25';
            audioElement.dataset.fadeoutduration = '2.75';
            audioElement.dataset.playlistdelay = '8.5';
            audioElement.dataset.durationremainingtriggernextmusic = '15.5';

            MusicElementFactory.fromAudioElement(audioElement);

            const calledDTO = (MusicElement as any).mock.calls[0][1] as MusicElementDTO;
            expect(calledDTO.defaultVolume).toBe(0.65);
            expect(calledDTO.fadeInDuration).toBe(1.25);
            expect(calledDTO.fadeOutDuration).toBe(2.75);
            expect(calledDTO.delay).toBe(8.5);
            expect(calledDTO.durationRemainingTriggerNextMusic).toBe(15.5);
        });
    });

    describe('fromButtonPlaylist', () => {
        let buttonElement: HTMLElement;
        let buttonPlaylist: ButtonPlaylist;

        beforeEach(() => {
            document.body.innerHTML = `
                <div id="audio-players"></div>
            `;

            buttonElement = document.createElement('div');
            buttonElement.id = 'playlist-789';
            buttonElement.dataset.playlistId = '789';
            buttonElement.dataset.playlistType = 'ambient';
            buttonElement.dataset.playlistVolume = '75';
            buttonElement.dataset.playlistFadein = 'true';
            buttonElement.dataset.playlistFadeintype = 'cubic';
            buttonElement.dataset.playlistFadeinduration = '3.5';
            buttonElement.dataset.playlistFadeout = 'true';
            buttonElement.dataset.playlistFadeouttype = 'quadratic';
            buttonElement.dataset.playlistFadeoutduration = '4.0';
            buttonElement.dataset.playlistLoop = 'true';
            buttonElement.dataset.playlistDelay = '7.5';
            buttonElement.dataset.playlistUri = 'https://example.com/ambient.mp3';
            buttonElement.dataset.playlistDurationremainingtriggernextmusic = '12.0';
            buttonElement.dataset.tokenPlaylistActive = 'active-token-456';

            buttonPlaylist = new ButtonPlaylist(buttonElement);
        });

        afterEach(() => {
            document.body.innerHTML = '';
        });

        it('should create a MusicElement from a ButtonPlaylist with all properties', () => {
            MusicElementFactory.fromButtonPlaylist(buttonPlaylist);

            expect(MusicElement).toHaveBeenCalledWith(
                expect.any(HTMLAudioElement),
                expect.objectContaining({
                    butonPlaylistToken: 'active-token-456',
                    defaultVolume: 0.75,
                    fadeIn: true,
                    fadeInType: 'cubic',
                    fadeInDuration: 3.5,
                    fadeOut: true,
                    fadeOutType: 'quadratic',
                    fadeOutDuration: 4,
                    playlistType: 'ambient',
                    idPlaylist: '789',
                    playlistLoop: true,
                    delay: 7.5,
                    baseUrl: 'https://example.com/ambient.mp3',
                    durationRemainingTriggerNextMusic: 12
                })
            );
        });

        it('should create an audio element with correct properties', () => {
            MusicElementFactory.fromButtonPlaylist(buttonPlaylist);

            const audioElement = (MusicElement as any).mock.calls[0][0] as HTMLAudioElement;
            expect(audioElement.tagName).toBe('AUDIO');
            expect(audioElement.className).toBe('playlist-audio-789 audio-ambient');
            expect(audioElement.classList.contains('playlist-audio-789')).toBe(true);
            expect(audioElement.classList.contains('audio-ambient')).toBe(true);
        });

        it('should set audio src with timestamp when not slave', () => {
            vi.mocked(SharedSoundBoardUtil.isSlavePage).mockReturnValue(false);
            
            MusicElementFactory.fromButtonPlaylist(buttonPlaylist);

            const audioElement = (MusicElement as any).mock.calls[0][0] as HTMLAudioElement;
            expect(audioElement.src).toMatch(/https:\/\/example\.com\/ambient\.mp3\?i=\d+/);
        });

        it('should set audio src without timestamp when slave', () => {
            vi.mocked(SharedSoundBoardUtil.isSlavePage).mockReturnValue(true);
            
            MusicElementFactory.fromButtonPlaylist(buttonPlaylist);

            const audioElement = (MusicElement as any).mock.calls[0][0] as HTMLAudioElement;
            expect(audioElement.src).toBe('https://example.com/ambient.mp3');
        });

        it('should set controls based on Config.DEBUG', () => {
            Config.DEBUG = true;
            let musicElement = MusicElementFactory.fromButtonPlaylist(buttonPlaylist);
            let audioElement = (MusicElement as any).mock.calls[0][0] as HTMLAudioElement;
            expect(audioElement.controls).toBe(true);

            vi.clearAllMocks();

            Config.DEBUG = false;
            musicElement = MusicElementFactory.fromButtonPlaylist(buttonPlaylist);
            audioElement = (MusicElement as any).mock.calls[0][0] as HTMLAudioElement;
            expect(audioElement.controls).toBe(false);
        });

        it('should set all data attributes on audio element', () => {
            MusicElementFactory.fromButtonPlaylist(buttonPlaylist);

            const audioElement = (MusicElement as any).mock.calls[0][0] as HTMLAudioElement;
            expect(audioElement.dataset.butonPlaylistToken).toBe('active-token-456');
            expect(audioElement.dataset.defaultvolume).toBe('0.75');
            expect(audioElement.dataset.fadein).toBe('true');
            expect(audioElement.dataset.fadeintype).toBe('cubic');
            expect(audioElement.dataset.fadeinduration).toBe('3.5');
            expect(audioElement.dataset.fadeout).toBe('true');
            expect(audioElement.dataset.fadeouttype).toBe('quadratic');
            expect(audioElement.dataset.fadeoutduration).toBe('4');
            expect(audioElement.dataset.playlisttype).toBe('ambient');
            expect(audioElement.dataset.playlistid).toBe('789');
            expect(audioElement.dataset.playlistloop).toBe('true');
            expect(audioElement.dataset.playlistdelay).toBe('7.5');
            expect(audioElement.dataset.baseurl).toBe('https://example.com/ambient.mp3');
            expect(audioElement.dataset.durationremainingtriggernextmusic).toBe('12');
        });

        it('should handle missing optional properties with defaults', () => {
            const minimalButton = document.createElement('div');
            minimalButton.dataset.playlistId = '999';
            minimalButton.dataset.playlistType = 'sfx';
            minimalButton.dataset.playlistUri = 'https://example.com/sfx.mp3';
            
            const minimalPlaylist = new ButtonPlaylist(minimalButton);

            MusicElementFactory.fromButtonPlaylist(minimalPlaylist);

            expect(MusicElement).toHaveBeenCalledWith(
                expect.any(HTMLAudioElement),
                expect.objectContaining({
                    butonPlaylistToken: null,
                    defaultVolume: 1,
                    fadeIn: false,
                    fadeInType: 'linear',
                    fadeInDuration: 0,
                    fadeOut: false,
                    fadeOutType: 'linear',
                    fadeOutDuration: 0,
                    playlistType: 'sfx',
                    idPlaylist: '999',
                    playlistLoop: false,
                    delay: 0,
                    baseUrl: 'https://example.com/sfx.mp3',
                    durationRemainingTriggerNextMusic: 0
                })
            );
        });

        it('should use Boolean.convert for boolean values from ButtonPlaylist', () => {
            buttonElement.dataset.playlistFadein = 'true';
            buttonElement.dataset.playlistFadeout = 'false';
            buttonElement.dataset.playlistLoop = 'true';

            const playlist = new ButtonPlaylist(buttonElement);
            MusicElementFactory.fromButtonPlaylist(playlist);

            expect(Boolean.convert).toHaveBeenCalledWith('true');
            expect(Boolean.convert).toHaveBeenCalledWith('false');
        });

        it('should calculate defaultVolume correctly from playlistVolume', () => {
            buttonElement.dataset.playlistVolume = '50';
            const playlist = new ButtonPlaylist(buttonElement);

            MusicElementFactory.fromButtonPlaylist(playlist);

            const calledDTO = (MusicElement as any).mock.calls[0][1] as MusicElementDTO;
            expect(calledDTO.defaultVolume).toBe(0.5); // 50 / 100
        });

        it('should not set butonPlaylistToken data attribute if token is null', () => {
            delete buttonElement.dataset.tokenPlaylistActive;
            const playlist = new ButtonPlaylist(buttonElement);

            MusicElementFactory.fromButtonPlaylist(playlist);

            const audioElement = (MusicElement as any).mock.calls[0][0] as HTMLAudioElement;
            expect(audioElement.dataset.butonPlaylistToken).toBeUndefined();
        });
    });

    describe('DTO validation', () => {
        it('should handle all required DTO properties', () => {
            const completeDTO: MusicElementDTO = {
                butonPlaylistToken: 'token-test',
                defaultVolume: 0.9,
                fadeIn: true,
                fadeInType: 'linear',
                fadeInDuration: 2.0,
                fadeOut: true,
                fadeOutType: 'linear',
                fadeOutDuration: 2,
                playlistType: 'music',
                idPlaylist: 'test-id',
                playlistLoop: true,
                delay: 1,
                baseUrl: 'http://test.com/music.mp3',
                durationRemainingTriggerNextMusic: 5
            };

            // Vérifier que toutes les propriétés sont définies
            expect(Object.keys(completeDTO)).toHaveLength(14);
        });
    });

    describe('edge cases', () => {
        it('should handle zero values correctly', () => {
            const audioElement = document.createElement('audio');
            audioElement.dataset.defaultvolume = '0';
            audioElement.dataset.fadeinduration = '0';
            audioElement.dataset.fadeoutduration = '0';
            audioElement.dataset.playlistdelay = '0';
            audioElement.dataset.durationremainingtriggernextmusic = '0';

            MusicElementFactory.fromAudioElement(audioElement);

            const calledDTO = (MusicElement as any).mock.calls[0][1] as MusicElementDTO;
            expect(calledDTO.defaultVolume).toBe(0);
            expect(calledDTO.fadeInDuration).toBe(0);
            expect(calledDTO.fadeOutDuration).toBe(0);
            expect(calledDTO.delay).toBe(0);
            expect(calledDTO.durationRemainingTriggerNextMusic).toBe(0);
        });

        it('should handle empty strings in dataset', () => {
            const audioElement = document.createElement('audio');
            audioElement.dataset.fadeintype = '';
            audioElement.dataset.fadeouttype = '';
            audioElement.dataset.playlisttype = '';
            audioElement.dataset.playlistid = '';
            audioElement.dataset.baseurl = '';

            MusicElementFactory.fromAudioElement(audioElement);

            const calledDTO = (MusicElement as any).mock.calls[0][1] as MusicElementDTO;
            // Les types de fade utilisent 'linear' par défaut si vide (via || 'linear')
            expect(calledDTO.fadeInType).toBe('linear');
            expect(calledDTO.fadeOutType).toBe('linear');
            // Les autres acceptent les chaînes vides
            expect(calledDTO.playlistType).toBe('');
            expect(calledDTO.idPlaylist).toBe('');
            expect(calledDTO.baseUrl).toBe('');
        });

        it('should handle very large numeric values', () => {
            const audioElement = document.createElement('audio');
            audioElement.dataset.defaultvolume = '999.999';
            audioElement.dataset.fadeinduration = '1000.5';
            audioElement.dataset.playlistdelay = '5000.75';

            MusicElementFactory.fromAudioElement(audioElement);

            const calledDTO = (MusicElement as any).mock.calls[0][1] as MusicElementDTO;
            expect(calledDTO.defaultVolume).toBe(999.999);
            expect(calledDTO.fadeInDuration).toBe(1000.5);
            expect(calledDTO.delay).toBe(5000.75);
        });

        it('should handle special characters in URLs', () => {
            const audioElement = document.createElement('audio');
            audioElement.dataset.baseurl = 'https://example.com/music/song%20name.mp3?param=value&other=123';

            MusicElementFactory.fromAudioElement(audioElement);

            const calledDTO = (MusicElement as any).mock.calls[0][1] as MusicElementDTO;
            expect(calledDTO.baseUrl).toBe('https://example.com/music/song%20name.mp3?param=value&other=123');
        });
    });

    describe('integration with ButtonPlaylist', () => {
        it('should create different audio elements for different playlist types', () => {
            const types = ['music', 'ambient', 'sfx', 'voice'];
            
            for (const [index, type] of types.entries()) {
                const buttonElement = document.createElement('div');
                buttonElement.dataset.playlistId = `${index}`;
                buttonElement.dataset.playlistType = type;
                buttonElement.dataset.playlistUri = `https://example.com/${type}.mp3`;
                
                const playlist = new ButtonPlaylist(buttonElement);
                MusicElementFactory.fromButtonPlaylist(playlist);

                const audioElement = (MusicElement as any).mock.calls[index][0] as HTMLAudioElement;
                expect(audioElement.classList.contains(`audio-${type}`)).toBe(true);
            }
        });

        it('should handle ButtonPlaylist with active token', () => {
            const buttonElement = document.createElement('div');
            buttonElement.dataset.playlistId = 'active-test';
            buttonElement.dataset.playlistType = 'music';
            buttonElement.dataset.playlistUri = 'https://example.com/music.mp3';
            buttonElement.classList.add('active-playlist');
            buttonElement.dataset.tokenPlaylistActive = Date.now().toString();
            
            const playlist = new ButtonPlaylist(buttonElement);
            MusicElementFactory.fromButtonPlaylist(playlist);

            const calledDTO = (MusicElement as any).mock.calls[0][1] as MusicElementDTO;
            expect(calledDTO.butonPlaylistToken).toBe(buttonElement.dataset.tokenPlaylistActive);
        });

        it('should handle ButtonPlaylist without active token', () => {
            const buttonElement = document.createElement('div');
            buttonElement.dataset.playlistId = 'inactive-test';
            buttonElement.dataset.playlistType = 'music';
            buttonElement.dataset.playlistUri = 'https://example.com/music.mp3';
            
            const playlist = new ButtonPlaylist(buttonElement);
            MusicElementFactory.fromButtonPlaylist(playlist);

            const calledDTO = (MusicElement as any).mock.calls[0][1] as MusicElementDTO;
            expect(calledDTO.butonPlaylistToken).toBeNull();
        });
    });

    describe('SharedSoundBoardUtil integration', () => {
        beforeEach(() => {
            document.body.innerHTML = '<div id="audio-players"></div>';
        });

        afterEach(() => {
            document.body.innerHTML = '';
        });

        it('should check isSlavePage when creating from ButtonPlaylist', () => {
            const buttonElement = document.createElement('div');
            buttonElement.dataset.playlistId = 'test';
            buttonElement.dataset.playlistType = 'music';
            buttonElement.dataset.playlistUri = 'https://example.com/music.mp3';
            
            const playlist = new ButtonPlaylist(buttonElement);
            
            vi.mocked(SharedSoundBoardUtil.isSlavePage).mockClear();
            MusicElementFactory.fromButtonPlaylist(playlist);

            expect(SharedSoundBoardUtil.isSlavePage).toHaveBeenCalled();
        });

        it('should append timestamp to URL for master page', () => {
            vi.mocked(SharedSoundBoardUtil.isSlavePage).mockReturnValue(false);
            
            const buttonElement = document.createElement('div');
            buttonElement.dataset.playlistId = 'master-test';
            buttonElement.dataset.playlistType = 'music';
            buttonElement.dataset.playlistUri = 'https://example.com/music.mp3';
            
            const playlist = new ButtonPlaylist(buttonElement);
            const before = Date.now();
            MusicElementFactory.fromButtonPlaylist(playlist);
            const after = Date.now();

            const audioElement = (MusicElement as any).mock.calls[0][0] as HTMLAudioElement;
            const urlMatch = audioElement.src.match(/\?i=(\d+)$/);
            
            expect(urlMatch).not.toBeNull();
            const timestamp = Number.parseInt(urlMatch![1]);
            expect(timestamp).toBeGreaterThanOrEqual(before);
            expect(timestamp).toBeLessThanOrEqual(after);
        });

        it('should not append timestamp to URL for slave page', () => {
            vi.mocked(SharedSoundBoardUtil.isSlavePage).mockReturnValue(true);
            
            const buttonElement = document.createElement('div');
            buttonElement.dataset.playlistId = 'slave-test';
            buttonElement.dataset.playlistType = 'music';
            buttonElement.dataset.playlistUri = 'https://example.com/music.mp3';
            
            const playlist = new ButtonPlaylist(buttonElement);
            MusicElementFactory.fromButtonPlaylist(playlist);

            const audioElement = (MusicElement as any).mock.calls[0][0] as HTMLAudioElement;
            expect(audioElement.src).toBe('https://example.com/music.mp3');
            expect(audioElement.src).not.toContain('?i=');
        });
    });
});
