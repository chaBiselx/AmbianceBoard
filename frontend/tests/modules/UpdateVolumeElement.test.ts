import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import UpdateVolumeElement from '@/modules/UpdateVolumeElement';
import { MusicElement } from '@/modules/MusicElement';
import { MixerManager } from '@/modules/MixerManager';
import { ButtonPlaylistFinder } from '@/modules/ButtonPlaylist';
import Cookie from '@/modules/General/Cookie';
import { SharedSoundboardIdFinder } from '@/modules/SharedSoundboardCustomVolume';

// Mock des modules externes
vi.mock('@/modules/MusicElement');
vi.mock('@/modules/MixerManager');
vi.mock('@/modules/ButtonPlaylist');
vi.mock('@/modules/General/Cookie');
vi.mock('@/modules/SharedSoundboardCustomVolume');

describe('UpdateVolumeElement', () => {
    let mockMusicElement: MusicElement;
    let mockAudioElement: HTMLAudioElement;
    let updateVolumeElement: UpdateVolumeElement;

    beforeEach(() => {
        // Création d'un élément audio mock
        mockAudioElement = document.createElement('audio') as HTMLAudioElement;
        mockAudioElement.volume = 1;

        // Création d'un MusicElement mock avec toutes les propriétés nécessaires
        mockMusicElement = {
            DOMElement: mockAudioElement,
            idPlaylist: 'playlist-123',
            playlistType: 'music',
            defaultVolume: 0.8,
            levelFade: 1,
        } as MusicElement;

        // Réinitialisation du cache statique avant chaque test
        // @ts-ignore - accès à une propriété privée pour les tests
        UpdateVolumeElement.mixerCache = {};

        updateVolumeElement = new UpdateVolumeElement(mockMusicElement);
    });

    afterEach(() => {
        vi.clearAllMocks();
    });

    describe('constructor', () => {
        it('should initialize with a MusicElement', () => {
            expect(updateVolumeElement.musicElement).toBe(mockMusicElement);
        });
    });

    describe('update', () => {
        beforeEach(() => {
            // Mock des différentes fonctions de récupération de volume
            vi.spyOn(MixerManager, 'getMixerValue').mockReturnValue(1);
            vi.mocked(ButtonPlaylistFinder.search).mockReturnValue(null);
            vi.mocked(SharedSoundboardIdFinder.findSoundBoardId).mockReturnValue(null);
            vi.mocked(Cookie.get).mockReturnValue(null);
        });

        it('should update volume with default values', () => {
            mockMusicElement.defaultVolume = 0.5;
            mockMusicElement.levelFade = 1;
            
            updateVolumeElement.update();

            // Volume attendu: 0.5 * 1.0 * 1.0 * 1.0 * 1.0 = 0.5
            expect(mockAudioElement.volume).toBe(0.5);
        });

        it('should apply fade level to volume', () => {
            mockMusicElement.defaultVolume = 0.8;
            mockMusicElement.levelFade = 0.5;
            
            updateVolumeElement.update();

            // Volume attendu: 0.8 * 0.5 * 1.0 * 1.0 * 1.0 = 0.4
            expect(mockAudioElement.volume).toBe(0.4);
        });

        it('should apply mixer general volume', () => {
            mockMusicElement.defaultVolume = 1;
            mockMusicElement.levelFade = 1;
            vi.spyOn(MixerManager, 'getMixerValue').mockImplementation((type: string) => {
                if (type === 'general') return 0.6;
                return 1;
            });
            
            updateVolumeElement.update();

            // Volume attendu: 1.0 * 1.0 * 0.6 * 1.0 * 1.0 = 0.6
            expect(mockAudioElement.volume).toBe(0.6);
        });

        it('should apply mixer type volume', () => {
            mockMusicElement.defaultVolume = 1;
            mockMusicElement.levelFade = 1;
            mockMusicElement.playlistType = 'music';
            vi.spyOn(MixerManager, 'getMixerValue').mockImplementation((type: string) => {
                if (type === 'general') return 1;
                if (type === 'music') return 0.7;
                return 1;
            });
            
            updateVolumeElement.update();

            // Volume attendu: 1.0 * 1.0 * 1.0 * 0.7 * 1.0 = 0.7
            expect(mockAudioElement.volume).toBe(0.7);
        });

        it('should apply shared custom volume from cookie', () => {
            mockMusicElement.defaultVolume = 1;
            mockMusicElement.levelFade = 1;
            mockMusicElement.idPlaylist = 'playlist-123';
            
            vi.mocked(SharedSoundboardIdFinder.findSoundBoardId).mockReturnValue('soundboard-456');
            vi.mocked(Cookie.get).mockReturnValue(JSON.stringify({ 'playlist-123': 50 }));
            
            updateVolumeElement.update();

            // Volume attendu: 1.0 * 1.0 * 1.0 * 1.0 * 0.5 = 0.5
            expect(mockAudioElement.volume).toBe(0.5);
        });

        it('should combine all volume factors', () => {
            mockMusicElement.defaultVolume = 0.8;
            mockMusicElement.levelFade = 0.9;
            mockMusicElement.playlistType = 'ambient';
            mockMusicElement.idPlaylist = 'playlist-789';
            
            vi.spyOn(MixerManager, 'getMixerValue').mockImplementation((type: string) => {
                if (type === 'general') return 0.6;
                if (type === 'ambient') return 0.5;
                return 1;
            });
            
            vi.mocked(SharedSoundboardIdFinder.findSoundBoardId).mockReturnValue('soundboard-001');
            vi.mocked(Cookie.get).mockReturnValue(JSON.stringify({ 'playlist-789': 80 }));
            
            updateVolumeElement.update();

            // Volume attendu: 0.8 * 0.9 * 0.6 * 0.5 * 0.8 = 0.17
            expect(mockAudioElement.volume).toBeCloseTo(0.17, 2);
        });

        it('should clamp volume to maximum of 1', () => {
            mockMusicElement.defaultVolume = 2.0; // Volume supérieur à 1
            mockMusicElement.levelFade = 1;
            
            updateVolumeElement.update();

            expect(mockAudioElement.volume).toBe(1);
        });

        it('should clamp volume to minimum of 0', () => {
            mockMusicElement.defaultVolume = -0.5; // Volume négatif
            mockMusicElement.levelFade = 1;
            
            updateVolumeElement.update();

            expect(mockAudioElement.volume).toBe(0);
        });

        it('should use ButtonPlaylistFinder when defaultVolume is not set', () => {
            mockMusicElement.defaultVolume = 0;
            const mockButton = {
                getVolume: vi.fn().mockReturnValue(0.75)
            };
            vi.mocked(ButtonPlaylistFinder.search).mockReturnValue(mockButton as any);
            
            updateVolumeElement.update();

            expect(ButtonPlaylistFinder.search).toHaveBeenCalledWith('playlist-123');
            expect(mockButton.getVolume).toHaveBeenCalled();
            // Volume attendu: 0.75 * 1.0 * 1.0 * 1.0 * 1.0 = 0.75
            expect(mockAudioElement.volume).toBe(0.75);
        });

        it('should return 1 for shared custom volume when soundboard not found', () => {
            mockMusicElement.defaultVolume = 0.5;
            mockMusicElement.levelFade = 1;
            
            vi.mocked(SharedSoundboardIdFinder.findSoundBoardId).mockReturnValue(null);
            
            updateVolumeElement.update();

            // SharedCustomVolume devrait être 1, donc: 0.5 * 1.0 * 1.0 * 1.0 * 1.0 = 0.5
            expect(mockAudioElement.volume).toBe(0.5);
        });

        it('should return 1 for shared custom volume when playlist not in cookie', () => {
            mockMusicElement.defaultVolume = 0.5;
            mockMusicElement.levelFade = 1;
            mockMusicElement.idPlaylist = 'playlist-999';
            
            vi.mocked(SharedSoundboardIdFinder.findSoundBoardId).mockReturnValue('soundboard-456');
            vi.mocked(Cookie.get).mockReturnValue(JSON.stringify({ 'playlist-123': 50 }));
            
            updateVolumeElement.update();

            // Playlist non trouvée dans le cookie, SharedCustomVolume = 1
            expect(mockAudioElement.volume).toBe(0.5);
        });
    });

    describe('clearCache', () => {
        beforeEach(() => {
            vi.spyOn(MixerManager, 'getMixerValue').mockReturnValue(1);
            vi.mocked(ButtonPlaylistFinder.search).mockReturnValue(null);
            vi.mocked(SharedSoundboardIdFinder.findSoundBoardId).mockReturnValue(null);
        });

        it('should clear specified key from cache', () => {
            mockMusicElement.defaultVolume = 0.8;
            
            // Premier appel pour remplir le cache
            updateVolumeElement.update();
            
            // Modification de la valeur par défaut
            mockMusicElement.defaultVolume = 0.5;
            
            // Nettoyage du cache
            const result = updateVolumeElement.clearCache('playlist-123');
            
            // Vérification que clearCache retourne l'instance (chaînage)
            expect(result).toBe(updateVolumeElement);
            
            // Second appel devrait utiliser la nouvelle valeur
            updateVolumeElement.update();
            expect(mockAudioElement.volume).toBe(0.5);
        });

        it('should clear general mixer from cache', () => {
            mockMusicElement.defaultVolume = 1; // Définir à 1.0 pour simplifier le calcul
            
            vi.spyOn(MixerManager, 'getMixerValue').mockImplementation((type: string) => {
                if (type === 'general') return 0.8;
                return 1;
            });
            
            // Premier appel
            updateVolumeElement.update();
            expect(mockAudioElement.volume).toBe(0.8);
            
            // Changement de la valeur du mixer
            vi.spyOn(MixerManager, 'getMixerValue').mockImplementation((type: string) => {
                if (type === 'general') return 0.5;
                return 1;
            });
            
            // Nettoyage du cache
            updateVolumeElement.clearCache('playlist-123');
            
            // Second appel devrait utiliser la nouvelle valeur
            updateVolumeElement.update();
            expect(mockAudioElement.volume).toBe(0.5);
        });

        it('should support method chaining', () => {
            const result = updateVolumeElement
                .clearCache('playlist-123')
                .clearCache('music');
            
            expect(result).toBe(updateVolumeElement);
        });
    });

    describe('cache behavior', () => {
        beforeEach(() => {
            vi.spyOn(MixerManager, 'getMixerValue').mockReturnValue(1);
            vi.mocked(ButtonPlaylistFinder.search).mockReturnValue(null);
            vi.mocked(SharedSoundboardIdFinder.findSoundBoardId).mockReturnValue(null);
        });

        it('should cache mixer values between calls', () => {
            const getMixerValueSpy = vi.spyOn(MixerManager, 'getMixerValue');
            
            updateVolumeElement.update();
            const firstCallCount = getMixerValueSpy.mock.calls.length;
            
            updateVolumeElement.update();
            const secondCallCount = getMixerValueSpy.mock.calls.length;
            
            // Le second appel ne devrait pas appeler getMixerValue car les valeurs sont en cache
            expect(secondCallCount).toBe(firstCallCount);
        });

        it('should cache default volume between calls', () => {
            const mockButton = {
                getVolume: vi.fn().mockReturnValue(0.75)
            };
            vi.mocked(ButtonPlaylistFinder.search).mockReturnValue(mockButton as any);
            mockMusicElement.defaultVolume = 0;
            
            updateVolumeElement.update();
            updateVolumeElement.update();
            
            // ButtonPlaylistFinder.search ne devrait être appelé qu'une fois grâce au cache
            expect(ButtonPlaylistFinder.search).toHaveBeenCalledTimes(1);
        });

        it('should share cache between instances', () => {
            const secondMusicElement = {
                DOMElement: document.createElement('audio') as HTMLAudioElement,
                idPlaylist: 'playlist-456',
                playlistType: 'music',
                defaultVolume: 0.9,
                levelFade: 1,
            } as MusicElement;
            
            const secondUpdateVolume = new UpdateVolumeElement(secondMusicElement);
            
            const getMixerValueSpy = vi.spyOn(MixerManager, 'getMixerValue');
            
            // Premier appel remplit le cache
            updateVolumeElement.update();
            
            // Second appel avec une autre instance devrait utiliser le cache
            getMixerValueSpy.mockClear();
            secondUpdateVolume.update();
            
            // Les valeurs de mixer général et type devraient être en cache
            expect(getMixerValueSpy).not.toHaveBeenCalledWith('general');
            expect(getMixerValueSpy).not.toHaveBeenCalledWith('music');
        });
    });

    describe('truncDecimal', () => {
        it('should truncate decimal values to 2 places', () => {
            mockMusicElement.defaultVolume = 0.123456;
            mockMusicElement.levelFade = 1;
            vi.spyOn(MixerManager, 'getMixerValue').mockReturnValue(1);
            vi.mocked(ButtonPlaylistFinder.search).mockReturnValue(null);
            vi.mocked(SharedSoundboardIdFinder.findSoundBoardId).mockReturnValue(null);
            
            updateVolumeElement.update();
            
            // Devrait être arrondi à 2 décimales: 0.12
            expect(mockAudioElement.volume).toBe(0.12);
        });

        it('should handle rounding up correctly', () => {
            mockMusicElement.defaultVolume = 0.555;
            mockMusicElement.levelFade = 1;
            vi.spyOn(MixerManager, 'getMixerValue').mockReturnValue(1);
            vi.mocked(ButtonPlaylistFinder.search).mockReturnValue(null);
            vi.mocked(SharedSoundboardIdFinder.findSoundBoardId).mockReturnValue(null);
            
            updateVolumeElement.update();
            
            // Devrait être arrondi à 0.56
            expect(mockAudioElement.volume).toBeCloseTo(0.56, 2);
        });
    });
});
