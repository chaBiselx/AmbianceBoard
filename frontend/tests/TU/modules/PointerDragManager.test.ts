import { beforeEach, describe, expect, it, vi } from 'vitest';
import { isPointerDragging, PointerDragManager } from '@/modules/SoundboardOrganizer/PointerDragManager';

const dropMocks = vi.hoisted(() => ({
    sectionDrop: vi.fn(),
    unassociatedDrop: vi.fn(),
}));

vi.mock('@/modules/SoundboardOrganizer/PlaylistDropHandler', () => ({
    PlaylistDropHandler: class {
        handleSectionDrop(...args: unknown[]) {
            dropMocks.sectionDrop(...args);
        }

        handleUnassociatedDrop(...args: unknown[]) {
            dropMocks.unassociatedDrop(...args);
        }
    },
}));

const pointerEvent = (type: string, pointerId: number, x: number, y: number, target?: EventTarget) => {
    const event = new MouseEvent(type, { bubbles: true, cancelable: true, button: 0, clientX: x, clientY: y });
    Object.defineProperties(event, {
        pointerId: { value: pointerId },
        pointerType: { value: 'mouse' },
    });
    (target ?? window).dispatchEvent(event);
    return event;
};

describe('PointerDragManager', () => {
    beforeEach(() => {
        vi.clearAllMocks();
        document.body.innerHTML = `
            <div class="section-container" data-section="3">
                <div id="playlist-1" class="playlist-dragAndDrop"></div>
            </div>
            <div id="section-zone" class="zone-dragAndDrop" data-section="4"></div>
            <div id="unassociated-playlists" class="zone-dragAndDrop"></div>
        `;
    });

    it('starts only after the movement threshold, dispatches both drop types, and resets state', () => {
        const playlist = document.getElementById('playlist-1')!;
        const sectionZone = document.getElementById('section-zone')!;
        const unassociatedZone = document.getElementById('unassociated-playlists')!;
        const elementFromPoint = vi.fn(() => sectionZone);
        Object.defineProperty(document, 'elementFromPoint', { configurable: true, value: elementFromPoint });

        new PointerDragManager().setupEvents();
        expect(playlist.draggable).toBe(false);
        expect(playlist.style.touchAction).toBe('none');

        const dragStart = new Event('dragstart', { bubbles: true, cancelable: true });
        playlist.dispatchEvent(dragStart);
        expect(dragStart.defaultPrevented).toBe(true);
        const dragOver = new Event('dragover', { bubbles: true, cancelable: true });
        sectionZone.dispatchEvent(dragOver);
        expect(dragOver.defaultPrevented).toBe(true);

        pointerEvent('pointerdown', 1, 10, 10, playlist);
        expect(isPointerDragging()).toBe(false);
        pointerEvent('pointermove', 1, 12, 12);
        expect(isPointerDragging()).toBe(false);
        pointerEvent('pointermove', 1, 20, 20);
        expect(isPointerDragging()).toBe(true);
        expect(document.querySelector('.drag-ghost')).not.toBeNull();
        expect(sectionZone.classList.contains('drag-over')).toBe(true);

        pointerEvent('pointerup', 1, 22, 22);
        expect(dropMocks.sectionDrop).toHaveBeenCalledWith(
            expect.any(MouseEvent),
            sectionZone,
            4,
            { id: 'playlist-1', dragstart: 'playlistAssociees-3' }
        );
        expect(isPointerDragging()).toBe(false);
        expect(document.querySelector('.drag-ghost')).toBeNull();
        expect(document.body.classList.contains('dragging-active')).toBe(false);

        elementFromPoint.mockReturnValue(unassociatedZone);
        pointerEvent('pointerdown', 2, 10, 10, playlist);
        pointerEvent('pointermove', 2, 20, 20);
        pointerEvent('pointerup', 2, 20, 20);

        expect(dropMocks.unassociatedDrop).toHaveBeenCalledWith(
            expect.any(MouseEvent),
            unassociatedZone,
            { id: 'playlist-1', dragstart: 'playlistAssociees-3' }
        );
        expect(isPointerDragging()).toBe(false);
    });
});