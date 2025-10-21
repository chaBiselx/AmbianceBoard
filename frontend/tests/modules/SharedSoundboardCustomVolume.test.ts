import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { SharedSoundboardCustomVolumeFactory, SharedSoundboardIdFinder } from '@/modules/SharedSoundboardCustomVolume';
import ModalCustom from '@/modules/General/Modal';
import Cookie from '@/modules/General/Cookie';

// Mock des modules externes
vi.mock('@/modules/General/Modal');
vi.mock('@/modules/General/Cookie');

describe('SharedSoundboardCustomVolume', () => {
    describe('SharedSoundboardIdFinder', () => {
        beforeEach(() => {
            document.body.innerHTML = '';
        });

        it('should return soundboard ID when element exists with valid dataset', () => {
            document.body.innerHTML = `
                <div id="template-shared-volume" data-shared-volume-soundboard-id="soundboard-123"></div>
            `;

            const result = SharedSoundboardIdFinder.findSoundBoardId('template-shared-volume');

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
            document.body.innerHTML = `
                <div id="template-empty-dataset" data-shared-volume-soundboard-id=""></div>
            `;

            const result = SharedSoundboardIdFinder.findSoundBoardId('template-empty-dataset');

            expect(result).toBeNull();
        });
    });

    describe('SharedSoundboardCustomVolumeFactory', () => {
        beforeEach(() => {
            document.body.innerHTML = '';
            vi.clearAllMocks();
        });

        it('should create instance when both elements exist and are valid', () => {
            document.body.innerHTML = `
                <div id="template-shared" data-shared-volume-soundboard-id="soundboard-456"></div>
                <button id="button-shared"></button>
            `;

            vi.mocked(Cookie.get).mockReturnValue(null);

            const result = SharedSoundboardCustomVolumeFactory.create('button-shared', 'template-shared');

            expect(result).not.toBeNull();
            expect(result?.cookieName).toBe('SharedPlaylistCustomVolume_soundboard-456');
        });

        it('should return null when template element does not exist', () => {
            document.body.innerHTML = `
                <button id="button-shared"></button>
            `;

            const result = SharedSoundboardCustomVolumeFactory.create('button-shared', 'non-existent-template');

            expect(result).toBeNull();
        });

        it('should return null when button element does not exist', () => {
            document.body.innerHTML = `
                <div id="template-shared" data-shared-volume-soundboard-id="soundboard-456"></div>
            `;

            const result = SharedSoundboardCustomVolumeFactory.create('non-existent-button', 'template-shared');

            expect(result).toBeNull();
        });

        it('should return null when template has no soundboard ID', () => {
            document.body.innerHTML = `
                <div id="template-shared"></div>
                <button id="button-shared"></button>
            `;

            const result = SharedSoundboardCustomVolumeFactory.create('button-shared', 'template-shared');

            expect(result).toBeNull();
        });

        it('should return null when button is not an HTMLButtonElement', () => {
            document.body.innerHTML = `
                <div id="template-shared" data-shared-volume-soundboard-id="soundboard-456"></div>
                <div id="button-shared"></div>
            `;

            const result = SharedSoundboardCustomVolumeFactory.create('button-shared', 'template-shared');

            expect(result).toBeNull();
        });
    });

    describe('SharedSoundboardCustomVolume', () => {
        let templateElement: HTMLElement;
        let buttonElement: HTMLButtonElement;
        let instance: any;

        beforeEach(() => {
            document.body.innerHTML = `
                <div id="template-shared" data-shared-volume-soundboard-id="soundboard-789">
                    <a class="playlist-link" data-playlist-id="playlist-1">
                        <img src="icon1.png" alt="Playlist 1">
                        <span>Playlist 1</span>
                    </a>
                    <a class="playlist-link" data-playlist-id="playlist-2">
                        <img src="icon2.png" alt="Playlist 2">
                        <span>Playlist 2</span>
                    </a>
                </div>
                <button id="button-shared"></button>
            `;

            vi.clearAllMocks();
            vi.mocked(Cookie.get).mockReturnValue(null);

            instance = SharedSoundboardCustomVolumeFactory.create('button-shared', 'template-shared');
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
                const rangeInputs = selector.querySelectorAll('input[type="range"]');

                expect(rangeInputs).toHaveLength(2);
                expect((rangeInputs[0] as HTMLInputElement).value).toBe('100');
                expect((rangeInputs[1] as HTMLInputElement).value).toBe('100');
            });

            it('should use existing cookie values for range inputs', () => {
                instance.jsonValue = { 'playlist-1': 60, 'playlist-2': 80 };

                const selector = instance.generateSelector();
                const rangeInputs = selector.querySelectorAll('input[type="range"]');

                expect((rangeInputs[0] as HTMLInputElement).value).toBe('60');
                expect((rangeInputs[1] as HTMLInputElement).value).toBe('80');
            });

            it('should set correct min and max values for range inputs', () => {
                const selector = instance.generateSelector();
                const rangeInputs = selector.querySelectorAll('input[type="range"]');

                rangeInputs.forEach((input: Element) => {
                    const htmlInput = input as HTMLInputElement;
                    expect(htmlInput.min).toBe('10');
                    expect(htmlInput.max).toBe('100');
                });
            });

            it('should clone only image elements from playlist links', () => {
                const selector = instance.generateSelector();
                const clonedLinks = selector.querySelectorAll('.playlist-link');

                clonedLinks.forEach((link: Element) => {
                    const images = link.querySelectorAll('img');
                    const spans = link.querySelectorAll('span');
                    expect(images.length).toBeGreaterThan(0);
                    expect(spans).toHaveLength(0); // Les spans doivent être supprimés
                });
            });

            it('should set correct data-idplaylist attribute on inputs', () => {
                const selector = instance.generateSelector();
                const rangeInputs = selector.querySelectorAll('input[type="range"]');

                expect((rangeInputs[0] as HTMLInputElement).dataset.idplaylist).toBe('playlist-1');
                expect((rangeInputs[1] as HTMLInputElement).dataset.idplaylist).toBe('playlist-2');
            });
        });

        describe('handleChangeForm', () => {
            it('should update cookie when form changes', () => {
                vi.mocked(Cookie.set).mockImplementation(() => {});

                const mockEvent = {
                    preventDefault: vi.fn(),
                    target: {
                        dataset: { idplaylist: 'playlist-1' },
                        value: '75'
                    }
                } as any;

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

                const mockEvent1 = {
                    preventDefault: vi.fn(),
                    target: {
                        dataset: { idplaylist: 'playlist-1' },
                        value: '60'
                    }
                } as any;

                const mockEvent2 = {
                    preventDefault: vi.fn(),
                    target: {
                        dataset: { idplaylist: 'playlist-2' },
                        value: '80'
                    }
                } as any;

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
                let callbackFn: (() => void) | null = null;

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
                mixerElements.forEach((el) => {
                    el.addEventListener = addEventListenerSpy;
                });

                // Exécuter le callback
                if (callbackFn) {
                    callbackFn();
                }

                expect(addEventListenerSpy).toHaveBeenCalledTimes(2);
                expect(addEventListenerSpy).toHaveBeenCalledWith('change', expect.any(Function));
            });
        });

        describe('edge cases', () => {
            it('should handle empty template', () => {
                document.body.innerHTML = `
                    <div id="template-empty" data-shared-volume-soundboard-id="soundboard-empty"></div>
                    <button id="button-empty"></button>
                `;

                vi.mocked(Cookie.get).mockReturnValue(null);
                const emptyInstance = SharedSoundboardCustomVolumeFactory.create('button-empty', 'template-empty');

                const selector = emptyInstance?.generateSelector();
                expect(selector?.querySelectorAll('.flex-item')).toHaveLength(0);
            });

            it('should handle minimum value boundary', () => {
                const selector = instance.generateSelector();
                const rangeInputs = selector.querySelectorAll('input[type="range"]');

                rangeInputs.forEach((input: Element) => {
                    expect((input as HTMLInputElement).min).toBe(instance.minValue.toString());
                });
            });

            it('should handle maximum value boundary', () => {
                const selector = instance.generateSelector();
                const rangeInputs = selector.querySelectorAll('input[type="range"]');

                rangeInputs.forEach((input: Element) => {
                    expect((input as HTMLInputElement).max).toBe('100');
                });
            });
        });
    });
});
