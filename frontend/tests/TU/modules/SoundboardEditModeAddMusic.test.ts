import { beforeEach, describe, expect, it, vi } from 'vitest';
import SoundboardEditMode from '@/modules/SoundBoardEditor/SoundboardEditMode';

const popupMocks = vi.hoisted(() => ({
    construct: vi.fn(),
    show: vi.fn(),
}));

vi.mock('@/modules/SoundBoardEditor/PopupAddMusicToSoundboard', () => ({
    default: class {
        constructor(url: string) {
            popupMocks.construct(url);
        }

        showIfValue() {
            popupMocks.show();
        }
    },
}));

const addMusicButtonMarkup = (url: string) => `
    <button type="button" class="soundboard-edit-add-music-button" data-soundboard-edit-add-music-url="${url}">
        <i class="fa-solid fa-music"></i>
    </button>
`;

describe('SoundboardEditMode add music buttons', () => {
    let board: HTMLElement;
    let editButton: HTMLButtonElement;

    beforeEach(() => {
        vi.clearAllMocks();
        document.body.innerHTML = `
            <div class="responsive-sections-container" data-soundboard-editable="true">
                <div class="flex-container">
                    <div class="flex-item" id="item-1">
                        <div class="playlist-link" id="playlist-1"></div>
                        ${addMusicButtonMarkup('/add-music/1')}
                    </div>
                </div>
            </div>
            <button id="btn-soundboard-edit-mode" type="button" data-url-panel="/panel"></button>
        `;
        board = document.querySelector('[data-soundboard-editable="true"]') as HTMLElement;
        editButton = document.getElementById('btn-soundboard-edit-mode') as HTMLButtonElement;
        new SoundboardEditMode().addEvent();
    });

    const clickAddMusic = (root: ParentNode = document) => {
        const button = root.querySelector('.soundboard-edit-add-music-button') as HTMLButtonElement;
        button.click();
        return button;
    };

    it('does not open the popup when edit mode is disabled', () => {
        clickAddMusic();

        expect(popupMocks.construct).not.toHaveBeenCalled();
        expect(popupMocks.show).not.toHaveBeenCalled();
    });

    it('opens the popup with the button url when edit mode is enabled', () => {
        editButton.click();

        clickAddMusic();

        expect(popupMocks.construct).toHaveBeenCalledWith('/add-music/1');
        expect(popupMocks.show).toHaveBeenCalledTimes(1);
    });

    it('opens the popup when clicking the inner icon', () => {
        editButton.click();

        (board.querySelector('.soundboard-edit-add-music-button i') as HTMLElement).click();

        expect(popupMocks.construct).toHaveBeenCalledWith('/add-music/1');
    });

    it('handles buttons inserted after initialization', () => {
        editButton.click();
        board.querySelector('.flex-container')!.insertAdjacentHTML(
            'beforeend',
            `<div class="flex-item" id="item-2">${addMusicButtonMarkup('/add-music/2')}</div>`
        );

        clickAddMusic(document.getElementById('item-2')!);

        expect(popupMocks.construct).toHaveBeenCalledWith('/add-music/2');
        expect(popupMocks.show).toHaveBeenCalledTimes(1);
    });

    it('ignores clicks elsewhere on the board', () => {
        editButton.click();

        (document.getElementById('playlist-1') as HTMLElement).click();

        expect(popupMocks.construct).not.toHaveBeenCalled();
    });

    it('stops the click propagation once handled', () => {
        const documentListener = vi.fn();
        document.addEventListener('click', documentListener);
        editButton.click();
        documentListener.mockClear();

        clickAddMusic();

        expect(documentListener).not.toHaveBeenCalled();
        document.removeEventListener('click', documentListener);
    });

    it('stops opening the popup once edit mode is disabled again', () => {
        editButton.click();
        editButton.click();

        clickAddMusic();

        expect(popupMocks.construct).not.toHaveBeenCalled();
    });

    it('ignores repeated clicks during the cooldown then accepts them again', () => {
        vi.useFakeTimers();
        editButton.click();

        const button = clickAddMusic();
        clickAddMusic();

        expect(popupMocks.show).toHaveBeenCalledTimes(1);
        expect(button.hasAttribute('disabled')).toBe(true);

        vi.advanceTimersByTime(300);

        expect(button.hasAttribute('disabled')).toBe(false);
        expect(button.dataset.clicked).toBeUndefined();
        clickAddMusic();
        expect(popupMocks.show).toHaveBeenCalledTimes(2);
        vi.useRealTimers();
    });
});
