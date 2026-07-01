import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { SearchMusicElement } from '@/modules/MusicElementSearcher';
import { ButtonPlaylist } from '@/modules/ButtonPlaylist';
import { MusicElementFactory } from '@/modules/MusicElementFactory';

// Mock des modules externes
vi.mock('@/modules/MusicElementFactory');
vi.mock('@/modules/MusicElement');

describe('SearchMusicElement', () => {

    beforeEach(() => {
        vi.clearAllMocks();
        document.body.innerHTML = '';
    });

    afterEach(() => {
        document.body.innerHTML = '';
    });

    describe('searchByButton', () => {
        let buttonPlaylist: ButtonPlaylist;

        beforeEach(() => {
            const buttonElement = document.createElement('div');
            buttonElement.dataset.playlistId = 'playlist-123';
            buttonElement.dataset.playlistType = 'music';
            buttonElement.dataset.playlistSingleconcurrentread = 'true';
            buttonPlaylist = new ButtonPlaylist(buttonElement);
        });

        it('should return an empty array when no audio elements are found', () => {
            const result = SearchMusicElement.searchByButton(buttonPlaylist);

            expect(result).toEqual([]);
            expect(result).toHaveLength(0);
        });

        it('should return MusicElement array when audio elements exist', () => {
            // Créer des éléments audio dans le DOM
            const audio1 = document.createElement('audio');
            audio1.className = 'playlist-audio-playlist-123';
            const audio2 = document.createElement('audio');
            audio2.className = 'playlist-audio-playlist-123';
            
            document.body.appendChild(audio1);
            document.body.appendChild(audio2);

            // Mock du retour de la factory
            const mockMusicElement1 = { id: 'music1' } as any;
            const mockMusicElement2 = { id: 'music2' } as any;
            vi.mocked(MusicElementFactory.fromAudioElement)
                .mockReturnValueOnce(mockMusicElement1)
                .mockReturnValueOnce(mockMusicElement2);

            const result = SearchMusicElement.searchByButton(buttonPlaylist);

            expect(result).toHaveLength(2);
            expect(result[0]).toBe(mockMusicElement1);
            expect(result[1]).toBe(mockMusicElement2);
            expect(MusicElementFactory.fromAudioElement).toHaveBeenCalledTimes(2);
            expect(MusicElementFactory.fromAudioElement).toHaveBeenCalledWith(audio1);
            expect(MusicElementFactory.fromAudioElement).toHaveBeenCalledWith(audio2);
        });

        it('should search by the correct class name based on playlist ID', () => {
            const audio1 = document.createElement('audio');
            audio1.className = 'playlist-audio-playlist-123';
            const audio2 = document.createElement('audio');
            audio2.className = 'playlist-audio-different-id';
            
            document.body.appendChild(audio1);
            document.body.appendChild(audio2);

            const mockMusicElement = { id: 'music1' } as any;
            vi.mocked(MusicElementFactory.fromAudioElement).mockReturnValue(mockMusicElement);

            const result = SearchMusicElement.searchByButton(buttonPlaylist);

            // Seul audio1 devrait être trouvé car il a la bonne classe
            expect(result).toHaveLength(1);
            expect(MusicElementFactory.fromAudioElement).toHaveBeenCalledWith(audio1);
            expect(MusicElementFactory.fromAudioElement).not.toHaveBeenCalledWith(audio2);
        });

        it('should handle single audio element', () => {
            const audio = document.createElement('audio');
            audio.className = 'playlist-audio-playlist-123';
            document.body.appendChild(audio);

            const mockMusicElement = { id: 'music1' } as any;
            vi.mocked(MusicElementFactory.fromAudioElement).mockReturnValue(mockMusicElement);

            const result = SearchMusicElement.searchByButton(buttonPlaylist);

            expect(result).toHaveLength(1);
            expect(result[0]).toBe(mockMusicElement);
        });

        it('should handle multiple audio elements with the same playlist ID', () => {
            // Créer plusieurs éléments audio avec le même ID de playlist
            for (let i = 0; i < 5; i++) {
                const audio = document.createElement('audio');
                audio.className = 'playlist-audio-playlist-123';
                document.body.appendChild(audio);
            }

            const mockMusicElement = { id: 'music' } as any;
            vi.mocked(MusicElementFactory.fromAudioElement).mockReturnValue(mockMusicElement);

            const result = SearchMusicElement.searchByButton(buttonPlaylist);

            expect(result).toHaveLength(5);
            expect(MusicElementFactory.fromAudioElement).toHaveBeenCalledTimes(5);
        });

        it('should work with different playlist IDs', () => {
            // Test avec un autre ID de playlist
            const otherButtonElement = document.createElement('div');
            otherButtonElement.dataset.playlistId = 'playlist-456';
            otherButtonElement.dataset.playlistType = 'ambient';
            otherButtonElement.dataset.playlistSingleconcurrentread = 'false';
            const otherButtonPlaylist = new ButtonPlaylist(otherButtonElement);

            const audio = document.createElement('audio');
            audio.className = 'playlist-audio-playlist-456';
            document.body.appendChild(audio);

            const mockMusicElement = { id: 'ambient1' } as any;
            vi.mocked(MusicElementFactory.fromAudioElement).mockReturnValue(mockMusicElement);

            const result = SearchMusicElement.searchByButton(otherButtonPlaylist);

            expect(result).toHaveLength(1);
            expect(MusicElementFactory.fromAudioElement).toHaveBeenCalledWith(audio);
        });

        it('should handle audio elements with multiple classes', () => {
            const audio = document.createElement('audio');
            audio.className = 'playlist-audio-playlist-123 audio-music some-other-class';
            document.body.appendChild(audio);

            const mockMusicElement = { id: 'music1' } as any;
            vi.mocked(MusicElementFactory.fromAudioElement).mockReturnValue(mockMusicElement);

            const result = SearchMusicElement.searchByButton(buttonPlaylist);

            expect(result).toHaveLength(1);
            expect(result[0]).toBe(mockMusicElement);
        });

        it('should not include elements without the correct class', () => {
            const audio1 = document.createElement('audio');
            audio1.className = 'playlist-audio-playlist-123';
            const audio2 = document.createElement('audio');
            audio2.className = 'some-other-class';
            const audio3 = document.createElement('audio');
            audio3.className = 'playlist-audio-999';

            document.body.appendChild(audio1);
            document.body.appendChild(audio2);
            document.body.appendChild(audio3);

            const mockMusicElement = { id: 'music1' } as any;
            vi.mocked(MusicElementFactory.fromAudioElement).mockReturnValue(mockMusicElement);

            const result = SearchMusicElement.searchByButton(buttonPlaylist);

            expect(result).toHaveLength(1);
            expect(MusicElementFactory.fromAudioElement).toHaveBeenCalledTimes(1);
            expect(MusicElementFactory.fromAudioElement).toHaveBeenCalledWith(audio1);
        });

        it('should preserve the order of audio elements', () => {
            const audio1 = document.createElement('audio');
            audio1.className = 'playlist-audio-playlist-123';
            audio1.dataset.order = '1';
            const audio2 = document.createElement('audio');
            audio2.className = 'playlist-audio-playlist-123';
            audio2.dataset.order = '2';
            const audio3 = document.createElement('audio');
            audio3.className = 'playlist-audio-playlist-123';
            audio3.dataset.order = '3';

            document.body.appendChild(audio1);
            document.body.appendChild(audio2);
            document.body.appendChild(audio3);

            vi.mocked(MusicElementFactory.fromAudioElement)
                .mockImplementation((audio: HTMLAudioElement) => ({ order: audio.dataset.order } as any));

            const result = SearchMusicElement.searchByButton(buttonPlaylist);

            expect(result).toHaveLength(3);
            expect(result[0].order).toBe('1');
            expect(result[1].order).toBe('2');
            expect(result[2].order).toBe('3');
        });

        it('should handle special characters in playlist ID', () => {
            const specialButtonElement = document.createElement('div');
            specialButtonElement.dataset.playlistId = 'playlist-123-abc_def';
            specialButtonElement.dataset.playlistType = 'music';
            specialButtonElement.dataset.playlistSingleconcurrentread = 'true';
            const specialButtonPlaylist = new ButtonPlaylist(specialButtonElement);

            const audio = document.createElement('audio');
            audio.className = 'playlist-audio-playlist-123-abc_def';
            document.body.appendChild(audio);

            const mockMusicElement = { id: 'music1' } as any;
            vi.mocked(MusicElementFactory.fromAudioElement).mockReturnValue(mockMusicElement);

            const result = SearchMusicElement.searchByButton(specialButtonPlaylist);

            expect(result).toHaveLength(1);
        });
    });
});
