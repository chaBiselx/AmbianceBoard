import { describe, it, expect, beforeEach, vi } from 'vitest';
import { SharedSoundboardCustomVolumeFactory, SharedSoundboardIdFinder } from '@/modules/SharedSoundboardCustomVolume';
import ModalCustom from '@/modules/General/Modal';
import Cookie from '@/modules/General/Cookie';

// Mock des modules externes
vi.mock('@/modules/General/Modal');
vi.mock('@/modules/General/Cookie');

// ========== HELPERS ==========
// NOSONAR
// SonarCloud: désactivation de l'analyse sur cette classe utilitaire de test
class TestHelpers {
    /**
     * Configure le DOM avec un template et un bouton
     */
    static setupDOM(options: {
        templateId?: string;
        buttonId?: string;
        soundboardId?: string;
        playlistCount?: number;
    } = {}) {
        const {
            templateId = 'template-shared',
            buttonId = 'button-shared',
            soundboardId = 'soundboard-789',
            playlistCount = 2
        } = options;

        const playlists = Array.from({ length: playlistCount }, (_, i) => `
            <a class="playlist-link" data-playlist-id="playlist-${i + 1}">
                <img src="icon${i + 1}.png" alt="Playlist ${i + 1}">
                <span>Playlist ${i + 1}</span>
            </a>
        `).join('');

        document.body.innerHTML = `
            <div id="${templateId}" ${soundboardId ? `data-shared-volume-soundboard-id="${soundboardId}"` : ''}>
                ${playlists}
            </div>
            <button id="${buttonId}"></button>
        `;
    }

    /**
     * Mock le cookie avec des valeurs par défaut
     */
    static mockCookie(value: string | null = null) {
        vi.mocked(Cookie.get).mockReturnValue(value);
        vi.mocked(Cookie.set).mockImplementation(() => {});
    }

    /**
     * Crée une instance avec configuration par défaut
     */
    static createInstance(buttonId = 'button-shared', templateId = 'template-shared') {
        return SharedSoundboardCustomVolumeFactory.create(buttonId, templateId);
    }

    /**
     * Crée un événement de changement simulé
     */
    static createChangeEvent(playlistId: string, value: string) {
        return {
            preventDefault: vi.fn(),
            target: {
                dataset: { idplaylist: playlistId },
                value
            }
        } as any;
    }

    /**
     * Vérifie les propriétés d'un input range
     */
    static verifyRangeInput(input: HTMLInputElement, expected: {
        min?: string;
        max?: string;
        value?: string;
        playlistId?: string;
    }) {
        if (expected.min) expect(input.min).toBe(expected.min);
        if (expected.max) expect(input.max).toBe(expected.max);
        if (expected.value) expect(input.value).toBe(expected.value);
        if (expected.playlistId) expect(input.dataset.idplaylist).toBe(expected.playlistId);
    }

    /**
     * Vérifie la valeur par défaut d'un input
     */
    static verifyDefaultValue(input: HTMLInputElement) {
        TestHelpers.verifyRangeInput(input, { value: '100' });
    }

    /**
     * Vérifie les valeurs min et max d'un input
     */
    static verifyMinMax(input: HTMLInputElement) {
        TestHelpers.verifyRangeInput(input, { min: '10', max: '100' });
    }

    /**
     * Vérifie le contenu d'un lien (images présentes, spans absents)
     */
    static verifyLinkContent(link: Element) {
        expect(link.querySelectorAll('img').length).toBeGreaterThan(0);
        expect(link.querySelectorAll('span')).toHaveLength(0);
    }

    /**
     * Attache un spy d'événement à un élément
     */
    static attachEventListenerSpy(el: Element, spy: any) {
        el.addEventListener = spy;
    }

    /**
     * Vérifie la limite minimale d'un input
     */
    static verifyMinBoundary(input: HTMLInputElement, minValue: number) {
        expect(input.min).toBe(minValue.toString());
    }

    /**
     * Vérifie la limite maximale d'un input
     */
    static verifyMaxBoundary(input: HTMLInputElement) {
        expect(input.max).toBe('100');
    }
}

// ========== TESTS ==========
describe('SharedSoundboardCustomVolume', () => {
    describe('SharedSoundboardIdFinder', () => {
        beforeEach(() => {
            document.body.innerHTML = '';
        });

        it('should return soundboard ID when element exists with valid dataset', () => {
            TestHelpers.setupDOM({ soundboardId: 'soundboard-123' });
            const result = SharedSoundboardIdFinder.findSoundBoardId('template-shared');
            expect(result).toBe('soundboard-123');
        });

        it('should return null when element does not exist', () => {
            const result = SharedSoundboardIdFinder.findSoundBoardId('non-existent-id');

            expect(result).toBeNull();
        });

        it('should return null when element exists but has no dataset', () => {
            document.body.innerHTML = `
                <div id="template-no-dataset"></div>
            `;

            const result = SharedSoundboardIdFinder.findSoundBoardId('template-no-dataset');

            expect(result).toBeNull();
        });

        it('should return null when element exists but dataset is empty', () => {
            TestHelpers.setupDOM({ soundboardId: '' });

            const result = SharedSoundboardIdFinder.findSoundBoardId('template-shared');

            expect(result).toBeNull();
        });
    });

    describe('SharedSoundboardCustomVolumeFactory', () => {
        beforeEach(() => {
            document.body.innerHTML = '';
            vi.clearAllMocks();
        });

        it('should create instance when both elements exist and are valid', () => {
            TestHelpers.setupDOM({ soundboardId: 'soundboard-456' });
            TestHelpers.mockCookie();

            const result = TestHelpers.createInstance();

            expect(result).not.toBeNull();
            expect(result?.cookieName).toBe('SharedPlaylistCustomVolume_soundboard-456');
        });

        it('should return null when template element does not exist', () => {
            document.body.innerHTML = `
                <button id="button-shared"></button>
            `;

            const result = TestHelpers.createInstance('button-shared', 'non-existent-template');

            expect(result).toBeNull();
        });

        it('should return null when button element does not exist', () => {
            TestHelpers.setupDOM({ soundboardId: 'soundboard-456', playlistCount: 0 });

            const result = TestHelpers.createInstance('non-existent-button', 'template-shared');

            expect(result).toBeNull();
        });

        it('should return null when template has no soundboard ID', () => {
            TestHelpers.setupDOM({ soundboardId: '' });

            const result = TestHelpers.createInstance();

            expect(result).toBeNull();
        });

        it('should return null when button is not an HTMLButtonElement', () => {
            document.body.innerHTML = `
                <div id="template-shared" data-shared-volume-soundboard-id="soundboard-456"></div>
                <div id="button-shared"></div>
            `;

            const result = TestHelpers.createInstance();

            expect(result).toBeNull();
        });
    });

    describe('SharedSoundboardCustomVolume', () => {
        let instance: any;

        beforeEach(() => {
            TestHelpers.setupDOM();
            vi.clearAllMocks();
            TestHelpers.mockCookie();
            instance = TestHelpers.createInstance();
        });

        describe('constructor', () => {
            it('should initialize with correct properties', () => {
                expect(instance).not.toBeNull();
                expect(instance.cookieName).toBe('SharedPlaylistCustomVolume_soundboard-789');
                expect(instance.jsonValue).toEqual({});
                expect(instance.minValue).toBe(10);
            });

            it('should load existing cookie data', () => {
                vi.mocked(Cookie.get).mockReturnValue(JSON.stringify({ 'playlist-1': 75, 'playlist-2': 50 }));

                const newInstance = SharedSoundboardCustomVolumeFactory.create('button-shared', 'template-shared');

                expect(newInstance?.jsonValue).toEqual({ 'playlist-1': 75, 'playlist-2': 50 });
            });

            it('should initialize with empty object when cookie is null', () => {
                vi.mocked(Cookie.get).mockReturnValue(null);

                const newInstance = SharedSoundboardCustomVolumeFactory.create('button-shared', 'template-shared');

                expect(newInstance?.jsonValue).toEqual({});
            });
        });

        describe('addEvent', () => {
            it('should add click event listener to button', () => {
                const addEventListenerSpy = vi.spyOn(instance.DOMButton, 'addEventListener');

                instance.addEvent();

                expect(addEventListenerSpy).toHaveBeenCalledTimes(1);
                expect(addEventListenerSpy).toHaveBeenCalledWith('click', expect.any(Function));
            });

            it('should trigger modal when button is clicked', () => {
                vi.mocked(ModalCustom.show).mockImplementation(() => {});

                instance.addEvent();
                instance.DOMButton.click();

                expect(ModalCustom.show).toHaveBeenCalledTimes(1);
                expect(ModalCustom.show).toHaveBeenCalledWith(
                    expect.objectContaining({
                        title: 'Reporting content',
                        width: 'xl',
                        footer: '',
                        callback: expect.any(Function)
                    })
                );
            });
        });

        describe('generateSelector', () => {
            it('should generate selector with all playlist links', () => {
                const selector = instance.generateSelector();

                expect(selector.classList.contains('flex-container')).toBe(true);
                expect(selector.querySelectorAll('.flex-item')).toHaveLength(2);
            });

            it('should create range inputs with correct default values', () => {
                const selector = instance.generateSelector();
                const rangeInputs = selector.querySelectorAll('input[type="range"]') as NodeListOf<HTMLInputElement>;

                expect(rangeInputs).toHaveLength(2);
                for (const input of rangeInputs) {
                    TestHelpers.verifyDefaultValue(input);
                }
            });

            it('should use existing cookie values for range inputs', () => {
                instance.jsonValue = { 'playlist-1': 60, 'playlist-2': 80 };

                const selector = instance.generateSelector();
                const rangeInputs = selector.querySelectorAll('input[type="range"]') as NodeListOf<HTMLInputElement>;

                TestHelpers.verifyRangeInput(rangeInputs[0], { value: '60' });
                TestHelpers.verifyRangeInput(rangeInputs[1], { value: '80' });
            });

            it('should set correct min and max values for range inputs', () => {
                const selector = instance.generateSelector();
                const rangeInputs = selector.querySelectorAll('input[type="range"]') as NodeListOf<HTMLInputElement>;

                for (const input of rangeInputs) {
                    TestHelpers.verifyMinMax(input);
                }
            });

            it('should clone only image elements from playlist links', () => {
                const selector = instance.generateSelector();
                const clonedLinks = selector.querySelectorAll('.playlist-link');

                for (const link of clonedLinks) {
                    TestHelpers.verifyLinkContent(link);
                }
            });

            it('should set correct data-idplaylist attribute on inputs', () => {
                const selector = instance.generateSelector();
                const rangeInputs = selector.querySelectorAll('input[type="range"]') as NodeListOf<HTMLInputElement>;

                TestHelpers.verifyRangeInput(rangeInputs[0], { playlistId: 'playlist-1' });
                TestHelpers.verifyRangeInput(rangeInputs[1], { playlistId: 'playlist-2' });
            });
        });

        describe('handleChangeForm', () => {
            it('should update cookie when form changes', () => {
                vi.mocked(Cookie.set).mockImplementation(() => {});

                const mockEvent = TestHelpers.createChangeEvent('playlist-1', '75');

                instance.handleChangeForm(mockEvent);

                expect(mockEvent.preventDefault).toHaveBeenCalled();
                expect(instance.jsonValue['playlist-1']).toBe(75);
                expect(Cookie.set).toHaveBeenCalledWith(
                    'SharedPlaylistCustomVolume_soundboard-789',
                    JSON.stringify({ 'playlist-1': 75 })
                );
            });

            it('should handle multiple changes correctly', () => {
                vi.mocked(Cookie.set).mockImplementation(() => {});

                const mockEvent1 = TestHelpers.createChangeEvent('playlist-1', '60');
                const mockEvent2 = TestHelpers.createChangeEvent('playlist-2', '80');

                instance.handleChangeForm(mockEvent1);
                instance.handleChangeForm(mockEvent2);

                expect(instance.jsonValue).toEqual({ 'playlist-1': 60, 'playlist-2': 80 });
                expect(Cookie.set).toHaveBeenCalledTimes(2);
            });
        });

        describe('setCookie', () => {
            it('should update jsonValue and save to cookie', () => {
                vi.mocked(Cookie.set).mockImplementation(() => {});

                instance.setCookie('playlist-3', 90);

                expect(instance.jsonValue['playlist-3']).toBe(90);
                expect(Cookie.set).toHaveBeenCalledWith(
                    'SharedPlaylistCustomVolume_soundboard-789',
                    JSON.stringify({ 'playlist-3': 90 })
                );
            });

            it('should preserve existing values when adding new ones', () => {
                vi.mocked(Cookie.set).mockImplementation(() => {});
                instance.jsonValue = { 'playlist-1': 50 };

                instance.setCookie('playlist-2', 70);

                expect(instance.jsonValue).toEqual({ 'playlist-1': 50, 'playlist-2': 70 });
            });

            it('should overwrite existing value for same playlist', () => {
                vi.mocked(Cookie.set).mockImplementation(() => {});
                instance.jsonValue = { 'playlist-1': 50 };

                instance.setCookie('playlist-1', 80);

                expect(instance.jsonValue['playlist-1']).toBe(80);
            });
        });

        describe('modal integration', () => {
            it('should show modal with correct parameters', () => {
                vi.mocked(ModalCustom.show).mockImplementation(() => {});

                instance.getElementsToUpdateVolume();

                expect(ModalCustom.show).toHaveBeenCalledWith(
                    expect.objectContaining({
                        title: 'Reporting content',
                        width: 'xl',
                        footer: ''
                    })
                );
            });

            it('should attach change event listeners in modal callback', () => {
                let callbackFn: any = null;

                vi.mocked(ModalCustom.show).mockImplementation((options: any) => {
                    callbackFn = options.callback;
                });

                instance.getElementsToUpdateVolume();

                // Simuler l'ajout d'éléments dans le DOM après l'ouverture du modal
                document.body.innerHTML += `
                    <input class="mixer-playlist-custom-shared-update" data-idplaylist="playlist-1" value="50" />
                    <input class="mixer-playlist-custom-shared-update" data-idplaylist="playlist-2" value="75" />
                `;

                const addEventListenerSpy = vi.fn();
                const mixerElements = document.querySelectorAll('.mixer-playlist-custom-shared-update');
                for(const el of mixerElements){
                    TestHelpers.attachEventListenerSpy(el, addEventListenerSpy);
                }

                // Exécuter le callback
                if (callbackFn) callbackFn();

                expect(addEventListenerSpy).toHaveBeenCalledTimes(2);
                expect(addEventListenerSpy).toHaveBeenCalledWith('change', expect.any(Function));
            });
        });

        describe('edge cases', () => {
            it('should handle empty template', () => {
                TestHelpers.setupDOM({ 
                    templateId: 'template-empty', 
                    buttonId: 'button-empty',
                    soundboardId: 'soundboard-empty',
                    playlistCount: 0 
                });
                TestHelpers.mockCookie();
                
                const emptyInstance = TestHelpers.createInstance('button-empty', 'template-empty');
                const selector = emptyInstance?.generateSelector();
                
                expect(selector?.querySelectorAll('.flex-item')).toHaveLength(0);
            });

            it('should handle minimum value boundary', () => {
                const selector = instance.generateSelector();
                const rangeInputs = selector.querySelectorAll('input[type="range"]') as NodeListOf<HTMLInputElement>;

                for (const input of rangeInputs) {
                    TestHelpers.verifyMinBoundary(input, instance.minValue);
                }
            });

            it('should handle maximum value boundary', () => {
                const selector = instance.generateSelector();
                const rangeInputs = selector.querySelectorAll('input[type="range"]') as NodeListOf<HTMLInputElement>;

                for (const input of rangeInputs) {
                    TestHelpers.verifyMaxBoundary(input);
                }
            });
        });
    });
});
