import { afterEach, describe, expect, it, vi } from 'vitest';

const organizerEntryMocks = vi.hoisted(() => ({
    addCommunityPlaylistEvent: vi.fn(),
    valid: vi.fn(),
}));

vi.mock('@/modules/SoundboardOrganizer/OrganizerDom', () => ({
    EmptyPlaylistChecker: { check: vi.fn() },
    OrganizerDragAndDropZone: { valid: organizerEntryMocks.valid },
}));
vi.mock('@/modules/SoundboardOrganizer/PlaylistOrder', () => ({
    CleanOrderHandler: class { resetBadge() {} },
}));
vi.mock('@/modules/SoundboardOrganizer/SectionAdder', () => ({
    SectionAdder: class { addEvent() {} },
    SectionDeleter: class { addEvent() {} },
    SectionRenamer: class { addEvent() {} },
    SectionSwapper: class { addEvent() {} },
}));
vi.mock('@/modules/SoundboardOrganizer/PointerDragManager', () => ({
    PointerDragManager: class { setupEvents() {} },
}));
vi.mock('@/modules/SoundboardOrganizer/ScrollManager', () => ({
    ScrollManager: class { addEvent() {} },
}));
vi.mock('@/modules/SoundboardOrganizer/CommunityPlaylistAdder', () => ({
    CommunityPlaylistAdder: class { addEvent() { organizerEntryMocks.addCommunityPlaylistEvent(); } },
}));

describe('SounboardOrganizer entry point', () => {
    afterEach(() => {
        vi.resetModules();
        vi.clearAllMocks();
    });

    it('initializes community playlist adding even when drag-and-drop zones are invalid', async () => {
        organizerEntryMocks.valid.mockReturnValue(false);
        await import('@/SounboardOrganizer');
        document.dispatchEvent(new Event('DOMContentLoaded'));

        expect(organizerEntryMocks.addCommunityPlaylistEvent).toHaveBeenCalledOnce();
    });
});
