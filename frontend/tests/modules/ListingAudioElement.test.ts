import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { ListingAudioElement } from '@/modules/MusicElementSearcher';
import { MusicElementFactory } from '@/modules/MusicElementFactory';

// Mock des modules externes
vi.mock('@/modules/MusicElementFactory');
vi.mock('@/modules/MusicElement');
vi.mock('@/modules/General/Config', () => ({
    default: {
        DEBUG: false,
        SOUNDBOARD_DIV_ID_PLAYERS: 'audio-players'
    }
}));

describe('ListingAudioElement', () => {

    beforeEach(() => {
        vi.clearAllMocks();
        document.body.innerHTML = '<div id="audio-players"></div>';
    });

    afterEach(() => {
        document.body.innerHTML = '';
    });

    describe('getListingAudioElement', () => {

        it('should return an empty array when no audio elements of the specified type exist', () => {
            const result = ListingAudioElement.getListingAudioElement('music');

            expect(result).toEqual([]);
            expect(result).toHaveLength(0);
        });

        it('should return MusicElement array for a specific type', () => {
            const audioDiv = document.getElementById('audio-players')!;
            
            const audio1 = document.createElement('audio');
            audio1.className = 'audio-music';
            const audio2 = document.createElement('audio');
            audio2.className = 'audio-music';
            
            audioDiv.appendChild(audio1);
            audioDiv.appendChild(audio2);

            const mockMusicElement1 = { id: 'music1' } as any;
            const mockMusicElement2 = { id: 'music2' } as any;
            vi.mocked(MusicElementFactory.fromAudioElement)
                .mockReturnValueOnce(mockMusicElement1)
                .mockReturnValueOnce(mockMusicElement2);

            const result = ListingAudioElement.getListingAudioElement('music');

            expect(result).toHaveLength(2);
            expect(result[0]).toBe(mockMusicElement1);
            expect(result[1]).toBe(mockMusicElement2);
            expect(MusicElementFactory.fromAudioElement).toHaveBeenCalledTimes(2);
        });

        it('should filter by type and not include other types', () => {
            const audioDiv = document.getElementById('audio-players')!;
            
            const musicAudio = document.createElement('audio');
            musicAudio.className = 'audio-music';
            const ambientAudio = document.createElement('audio');
            ambientAudio.className = 'audio-ambient';
            const sfxAudio = document.createElement('audio');
            sfxAudio.className = 'audio-sfx';
            
            audioDiv.appendChild(musicAudio);
            audioDiv.appendChild(ambientAudio);
            audioDiv.appendChild(sfxAudio);

            const mockMusicElement = { type: 'music' } as any;
            vi.mocked(MusicElementFactory.fromAudioElement).mockReturnValue(mockMusicElement);

            const result = ListingAudioElement.getListingAudioElement('music');

            expect(result).toHaveLength(1);
            expect(MusicElementFactory.fromAudioElement).toHaveBeenCalledTimes(1);
            expect(MusicElementFactory.fromAudioElement).toHaveBeenCalledWith(musicAudio);
        });

        it('should work with different playlist types', () => {
            const audioDiv = document.getElementById('audio-players')!;
            
            const types = ['music', 'ambient', 'sfx', 'voice'];

            for (const type of types) {
                const audio = document.createElement('audio');
                audio.className = `audio-${type}`;
                audioDiv.appendChild(audio);
            }

            const mockMusicElement = { type: 'ambient' } as any;
            vi.mocked(MusicElementFactory.fromAudioElement).mockReturnValue(mockMusicElement);

            const result = ListingAudioElement.getListingAudioElement('ambient');

            expect(result).toHaveLength(1);
        });

        it('should handle multiple audio elements of the same type', () => {
            const audioDiv = document.getElementById('audio-players')!;
            
            for (let i = 0; i < 5; i++) {
                const audio = document.createElement('audio');
                audio.className = 'audio-sfx';
                audioDiv.appendChild(audio);
            }

            const mockMusicElement = { type: 'sfx' } as any;
            vi.mocked(MusicElementFactory.fromAudioElement).mockReturnValue(mockMusicElement);

            const result = ListingAudioElement.getListingAudioElement('sfx');

            expect(result).toHaveLength(5);
            expect(MusicElementFactory.fromAudioElement).toHaveBeenCalledTimes(5);
        });

        it('should handle audio elements with multiple classes', () => {
            const audioDiv = document.getElementById('audio-players')!;
            
            const audio = document.createElement('audio');
            audio.className = 'audio-music playlist-audio-123 some-other-class';
            audioDiv.appendChild(audio);

            const mockMusicElement = { id: 'music1' } as any;
            vi.mocked(MusicElementFactory.fromAudioElement).mockReturnValue(mockMusicElement);

            const result = ListingAudioElement.getListingAudioElement('music');

            expect(result).toHaveLength(1);
            expect(result[0]).toBe(mockMusicElement);
        });

        it('should only search within the audio-players div', () => {
            // Créer un audio en dehors de audio-players
            const outsideAudio = document.createElement('audio');
            outsideAudio.className = 'audio-music';
            document.body.appendChild(outsideAudio);

            const audioDiv = document.getElementById('audio-players')!;
            const insideAudio = document.createElement('audio');
            insideAudio.className = 'audio-music';
            audioDiv.appendChild(insideAudio);

            const mockMusicElement = { id: 'music1' } as any;
            vi.mocked(MusicElementFactory.fromAudioElement).mockReturnValue(mockMusicElement);

            const result = ListingAudioElement.getListingAudioElement('music');

            // getElementsByClassName cherche dans audioDiv, donc seul insideAudio est trouvé
            expect(result).toHaveLength(1);
            expect(MusicElementFactory.fromAudioElement).toHaveBeenCalledTimes(1);
            expect(MusicElementFactory.fromAudioElement).toHaveBeenCalledWith(insideAudio);
        });

        it('should preserve the order of audio elements', () => {
            const audioDiv = document.getElementById('audio-players')!;
            
            const audio1 = document.createElement('audio');
            audio1.className = 'audio-music';
            audio1.dataset.order = '1';
            const audio2 = document.createElement('audio');
            audio2.className = 'audio-music';
            audio2.dataset.order = '2';
            const audio3 = document.createElement('audio');
            audio3.className = 'audio-music';
            audio3.dataset.order = '3';

            audioDiv.appendChild(audio1);
            audioDiv.appendChild(audio2);
            audioDiv.appendChild(audio3);

            vi.mocked(MusicElementFactory.fromAudioElement)
                .mockImplementation((audio: HTMLAudioElement) => ({ order: audio.dataset.order } as any));

            const result = ListingAudioElement.getListingAudioElement('music');

            expect(result).toHaveLength(3);
            expect(result[0].order).toBe('1');
            expect(result[1].order).toBe('2');
            expect(result[2].order).toBe('3');
        });
    });

    describe('getListAllAudio', () => {

        it('should return an empty array when no audio elements exist', () => {
            const result = ListingAudioElement.getListAllAudio();

            expect(result).toEqual([]);
            expect(result).toHaveLength(0);
        });

        it('should return all audio elements regardless of type', () => {
            const audioDiv = document.getElementById('audio-players')!;
            
            const musicAudio = document.createElement('audio');
            musicAudio.className = 'audio-music';
            const ambientAudio = document.createElement('audio');
            ambientAudio.className = 'audio-ambient';
            const sfxAudio = document.createElement('audio');
            sfxAudio.className = 'audio-sfx';
            
            audioDiv.appendChild(musicAudio);
            audioDiv.appendChild(ambientAudio);
            audioDiv.appendChild(sfxAudio);

            vi.mocked(MusicElementFactory.fromAudioElement)
                .mockImplementation((audio: HTMLAudioElement) => ({ className: audio.className } as any));

            const result = ListingAudioElement.getListAllAudio();

            expect(result).toHaveLength(3);
            expect(MusicElementFactory.fromAudioElement).toHaveBeenCalledTimes(3);
            expect(MusicElementFactory.fromAudioElement).toHaveBeenCalledWith(musicAudio);
            expect(MusicElementFactory.fromAudioElement).toHaveBeenCalledWith(ambientAudio);
            expect(MusicElementFactory.fromAudioElement).toHaveBeenCalledWith(sfxAudio);
        });

        it('should return audio elements even without any class', () => {
            const audioDiv = document.getElementById('audio-players')!;
            
            const audio1 = document.createElement('audio');
            const audio2 = document.createElement('audio');
            
            audioDiv.appendChild(audio1);
            audioDiv.appendChild(audio2);

            const mockMusicElement = { id: 'audio' } as any;
            vi.mocked(MusicElementFactory.fromAudioElement).mockReturnValue(mockMusicElement);

            const result = ListingAudioElement.getListAllAudio();

            expect(result).toHaveLength(2);
        });

        it('should handle a single audio element', () => {
            const audioDiv = document.getElementById('audio-players')!;
            
            const audio = document.createElement('audio');
            audioDiv.appendChild(audio);

            const mockMusicElement = { id: 'single' } as any;
            vi.mocked(MusicElementFactory.fromAudioElement).mockReturnValue(mockMusicElement);

            const result = ListingAudioElement.getListAllAudio();

            expect(result).toHaveLength(1);
            expect(result[0]).toBe(mockMusicElement);
        });

        it('should handle many audio elements', () => {
            const audioDiv = document.getElementById('audio-players')!;
            
            for (let i = 0; i < 10; i++) {
                const audio = document.createElement('audio');
                audio.className = `audio-type${i % 3}`;
                audioDiv.appendChild(audio);
            }

            const mockMusicElement = { id: 'audio' } as any;
            vi.mocked(MusicElementFactory.fromAudioElement).mockReturnValue(mockMusicElement);

            const result = ListingAudioElement.getListAllAudio();

            expect(result).toHaveLength(10);
            expect(MusicElementFactory.fromAudioElement).toHaveBeenCalledTimes(10);
        });

        it('should only return audio elements from audio-players div', () => {
            // Audio en dehors
            const outsideAudio = document.createElement('audio');
            document.body.appendChild(outsideAudio);

            const audioDiv = document.getElementById('audio-players')!;
            const insideAudio1 = document.createElement('audio');
            const insideAudio2 = document.createElement('audio');
            audioDiv.appendChild(insideAudio1);
            audioDiv.appendChild(insideAudio2);

            const mockMusicElement = { id: 'audio' } as any;
            vi.mocked(MusicElementFactory.fromAudioElement).mockReturnValue(mockMusicElement);

            const result = ListingAudioElement.getListAllAudio();

            // getElementsByTagName cherche dans audioDiv, donc seuls les 2 audios internes sont trouvés
            expect(result).toHaveLength(2);
            expect(MusicElementFactory.fromAudioElement).toHaveBeenCalledTimes(2);
        });

        it('should preserve the order of all audio elements', () => {
            const audioDiv = document.getElementById('audio-players')!;
            
            const audio1 = document.createElement('audio');
            audio1.dataset.index = '1';
            const audio2 = document.createElement('audio');
            audio2.dataset.index = '2';
            const audio3 = document.createElement('audio');
            audio3.dataset.index = '3';

            audioDiv.appendChild(audio1);
            audioDiv.appendChild(audio2);
            audioDiv.appendChild(audio3);

            vi.mocked(MusicElementFactory.fromAudioElement)
                .mockImplementation((audio: HTMLAudioElement) => ({ index: audio.dataset.index } as any));

            const result = ListingAudioElement.getListAllAudio();

            expect(result).toHaveLength(3);
            expect(result[0].index).toBe('1');
            expect(result[1].index).toBe('2');
            expect(result[2].index).toBe('3');
        });

        it('should work with audio elements that have various attributes', () => {
            const audioDiv = document.getElementById('audio-players')!;
            
            const audio1 = document.createElement('audio');
            audio1.src = 'music1.mp3';
            audio1.controls = true;
            
            const audio2 = document.createElement('audio');
            audio2.src = 'music2.mp3';
            audio2.loop = true;
            
            audioDiv.appendChild(audio1);
            audioDiv.appendChild(audio2);

            vi.mocked(MusicElementFactory.fromAudioElement)
                .mockImplementation((audio: HTMLAudioElement) => ({ controls: audio.controls, loop: audio.loop } as any));

            const result = ListingAudioElement.getListAllAudio();

            expect(result).toHaveLength(2);
            expect(result[0].controls).toBe(true);
            expect(result[0].loop).toBeFalsy();
            expect(result[1].controls).toBeFalsy();
            expect(result[1].loop).toBe(true);
        });
    });

    describe('integration between getListingAudioElement and getListAllAudio', () => {

        it('should return subset with getListingAudioElement vs all with getListAllAudio', () => {
            const audioDiv = document.getElementById('audio-players')!;
            
            const musicAudio1 = document.createElement('audio');
            musicAudio1.className = 'audio-music';
            const musicAudio2 = document.createElement('audio');
            musicAudio2.className = 'audio-music';
            const ambientAudio = document.createElement('audio');
            ambientAudio.className = 'audio-ambient';
            
            audioDiv.appendChild(musicAudio1);
            audioDiv.appendChild(musicAudio2);
            audioDiv.appendChild(ambientAudio);

            const mockMusicElement = { id: 'audio' } as any;
            vi.mocked(MusicElementFactory.fromAudioElement).mockReturnValue(mockMusicElement);

            const musicResults = ListingAudioElement.getListingAudioElement('music');
            vi.clearAllMocks();
            vi.mocked(MusicElementFactory.fromAudioElement).mockReturnValue(mockMusicElement);
            
            const allResults = ListingAudioElement.getListAllAudio();

            expect(musicResults).toHaveLength(2);
            expect(allResults).toHaveLength(3);
        });

        it('should handle empty div consistently', () => {
            const musicResults = ListingAudioElement.getListingAudioElement('music');
            const allResults = ListingAudioElement.getListAllAudio();

            expect(musicResults).toHaveLength(0);
            expect(allResults).toHaveLength(0);
        });
    });

    describe('edge cases', () => {

        it('should handle when audio-players div does not exist', () => {
            document.body.innerHTML = '';

            // getListingAudioElement devrait échouer car getElementById retourne null
            expect(() => {
                ListingAudioElement.getListingAudioElement('music');
            }).toThrow();
        });

        it('should handle when audio-players div exists but is empty', () => {
            const audioDiv = document.getElementById('audio-players')!;
            expect(audioDiv.children.length).toBe(0);

            const result = ListingAudioElement.getListAllAudio();
            expect(result).toHaveLength(0);
        });

        it('should handle type with special characters', () => {
            const audioDiv = document.getElementById('audio-players')!;
            
            const audio = document.createElement('audio');
            audio.className = 'audio-music-special_type-123';
            audioDiv.appendChild(audio);

            const mockMusicElement = { id: 'special' } as any;
            vi.mocked(MusicElementFactory.fromAudioElement).mockReturnValue(mockMusicElement);

            const result = ListingAudioElement.getListingAudioElement('music-special_type-123');

            expect(result).toHaveLength(1);
        });
    });
});
