import { beforeEach, describe, expect, it } from 'vitest';
import SoundboardEditMode from '@/modules/SoundBoardEditor/SoundboardEditMode';

describe('SoundboardEditMode', () => {
    beforeEach(() => {
        document.body.innerHTML = '';
    });

    const setupBoard = ({ hasPlaylist = false }: { hasPlaylist?: boolean } = {}) => {
        const sections = document.createElement('div');
        sections.className = 'responsive-sections-container';

        if (hasPlaylist) {
            const playlistLink = document.createElement('a');
            playlistLink.className = 'playlist-link';
            sections.appendChild(playlistLink);
        }

        const board = document.createElement('div');
        board.setAttribute('data-soundboard-editable', 'true');

        const button = document.createElement('button');
        button.id = 'btn-soundboard-edit-mode';
        button.type = 'button';
        button.dataset.urlPanel = '/fake-panel/';

        document.body.appendChild(sections);
        document.body.appendChild(board);
        document.body.appendChild(button);

        return {
            board,
            button,
        };
    };

    it('enables edit mode automatically when there is no playlist on the board', () => {
        const { board, button } = setupBoard({ hasPlaylist: false });

        new SoundboardEditMode().addEvent();

        expect(board.classList.contains('soundboard-edit-mode-active')).toBe(true);
        expect(button.getAttribute('aria-pressed')).toBe('true');
        expect(button.classList.contains('btn-success')).toBe(true);
    });

    it('keeps edit mode disabled until the user clicks the action button when playlists already exist', () => {
        const { board, button } = setupBoard({ hasPlaylist: true });

        new SoundboardEditMode().addEvent();

        expect(board.classList.contains('soundboard-edit-mode-active')).toBe(false);
        expect(button.getAttribute('aria-pressed')).toBe('false');

        button.click();

        expect(board.classList.contains('soundboard-edit-mode-active')).toBe(true);
        expect(button.getAttribute('aria-pressed')).toBe('true');
    });
});
