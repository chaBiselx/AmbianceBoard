import { beforeEach, describe, expect, it, vi } from 'vitest';
import { SectionAdder, SectionDeleter, SectionRenamer } from '@/modules/SoundboardOrganizer/SectionAdder';

const sectionMocks = vi.hoisted(() => ({
    insert: vi.fn(),
    delete: vi.fn(),
    rename: vi.fn(),
    getMaxSections: vi.fn(),
    getNextSectionNumber: vi.fn(),
    refreshMaxSections: vi.fn(),
    getSectionNumbers: vi.fn(),
    associatedSection: vi.fn(),
    checkEmpty: vi.fn(),
    resetBadge: vi.fn(),
    modalShow: vi.fn(),
    modalHide: vi.fn(),
    consoleError: vi.fn(),
    consoleInfo: vi.fn(),
}));

vi.mock('@/modules/SoundboardOrganizer/OrganizerApi', () => ({
    SendBackendAction: class {
        insertSection(position: number) { return sectionMocks.insert(position); }
        deleteSection(position: number) { return sectionMocks.delete(position); }
        renameSection(position: number, name: string) { return sectionMocks.rename(position, name); }
    },
}));

vi.mock('@/modules/SoundboardOrganizer/OrganizerDom', () => ({
    SectionConfig: {
        getMaxSections: sectionMocks.getMaxSections,
        getNextSectionNumber: sectionMocks.getNextSectionNumber,
        refreshMaxSections: sectionMocks.refreshMaxSections,
        getSectionNumbers: sectionMocks.getSectionNumbers,
    },
    OrganizerDragAndDropZone: {
        associatedPlaylistsSection: sectionMocks.associatedSection,
    },
    EmptyPlaylistChecker: { check: sectionMocks.checkEmpty },
}));

vi.mock('@/modules/SoundboardOrganizer/PlaylistOrder', () => ({
    CleanOrderHandler: class {
        resetBadge() { sectionMocks.resetBadge(); return this; }
    },
}));

vi.mock('@/modules/General/Modal', () => ({
    default: { show: sectionMocks.modalShow, hide: sectionMocks.modalHide },
}));

vi.mock('@/modules/General/ConsoleCustom', () => ({ default: { error: sectionMocks.consoleError } }));
vi.mock('@/modules/General/ConsoleTesteur', () => ({
    default: { error: sectionMocks.consoleError, info: sectionMocks.consoleInfo },
}));

const accordion = (section: number, title = `Section ${section}`) => `
    <div class="accordion">
        <h2 class="accordion-header" id="panelsSection-${section}">
            <button class="accordion-button" aria-controls="panelsStayOpen-${section}"></button>
        </h2>
        <div class="accordion-collapse" id="panelsStayOpen-${section}">
            <div class="section-container" id="associated-playlists-section-${section}" data-section="${section}">
                <span class="section-${section}-empty"></span>
            </div>
        </div>
        <span class="num-section">${section}</span>
        <span class="section-title">${title}</span>
        <button class="section-edit-button" data-num-section="${section}"></button>
        <button class="section-insert-before-button" data-num-section="${section}"></button>
        <button class="section-delete-button" data-num-section="${section}"></button>
    </div>
`;

const setupContainer = (sections: string) => {
    document.body.innerHTML = `
        <div id="associated-playlists-container" data-section-default-title="My section"
            data-section-delete-confirmation="Delete section?" data-section-rename-cancel="Cancel" data-section-rename-save="Save">
            ${sections}
        </div>
        <div id="unassociated-playlists"></div>
        <template id="add-section-template" data-max-section="5">${accordion(0)}</template>
        <template id="rename-section-template"><form id="rename-section-form"><input id="rename-section-input"></form></template>
        <button id="add-section-button"></button>
    `;
};

describe('soundboard section controls', () => {
    beforeEach(() => {
        vi.clearAllMocks();
        sectionMocks.getMaxSections.mockReturnValue(1);
        sectionMocks.getNextSectionNumber.mockReturnValue(2);
        sectionMocks.getSectionNumbers.mockReturnValue([1]);
        sectionMocks.associatedSection.mockImplementation((section: number) =>
            document.getElementById(`associated-playlists-section-${section}`)
        );
        sectionMocks.insert.mockResolvedValue(true);
        sectionMocks.delete.mockResolvedValue(true);
        sectionMocks.rename.mockResolvedValue(true);
    });

    it('inserts a new section from the toolbar and updates its accordion metadata', async () => {
        setupContainer(accordion(1));
        const setupDragEvents = vi.fn();
        new SectionAdder(setupDragEvents).addEvent();

        document.getElementById('add-section-button')!.click();

        await vi.waitFor(() => expect(sectionMocks.insert).toHaveBeenCalledWith(2));
        const section = document.getElementById('associated-playlists-section-2')!;
        expect(section.dataset.section).toBe('2');
        expect(section.closest('.accordion')!.querySelector('.section-title')!.textContent).toBe(' My section 2');
        expect(setupDragEvents).toHaveBeenCalledOnce();
        expect(sectionMocks.checkEmpty).toHaveBeenCalledOnce();
        expect(sectionMocks.resetBadge).toHaveBeenCalledOnce();
    });

    it('deletes a confirmed section and shifts the remaining accordion identifiers', async () => {
        setupContainer(accordion(1) + accordion(2, 'Keep this title'));
        sectionMocks.getMaxSections.mockReturnValue(2);
        const confirmMock = vi.fn(() => true);
        vi.stubGlobal('confirm', confirmMock);
        const setupDragEvents = vi.fn();
        new SectionDeleter(setupDragEvents).addEvent();

        document.querySelector<HTMLButtonElement>('.section-delete-button')!.click();

        await vi.waitFor(() => expect(sectionMocks.delete).toHaveBeenCalledWith(1));
        expect(confirmMock).toHaveBeenCalledWith('Delete section?');
        expect(document.querySelectorAll('.accordion')).toHaveLength(1);
        expect(document.getElementById('associated-playlists-section-1')).not.toBeNull();
        expect(document.querySelector('.section-title')!.textContent).toBe('Keep this title');
        expect(setupDragEvents).toHaveBeenCalledOnce();
        expect(sectionMocks.resetBadge).toHaveBeenCalledOnce();
    });

    it('renames a section from the modal and leaves the name unchanged for blank input', async () => {
        setupContainer(accordion(1, 'Old title'));
        const modalBody = '<form id="rename-section-form"><input id="rename-section-input"></form>';
        sectionMocks.modalShow.mockImplementation((options: { body: string }) => {
            document.body.insertAdjacentHTML('beforeend', options.body || modalBody);
        });
        const manager = new SectionRenamer();
        manager.addEvent();

        document.querySelector<HTMLButtonElement>('.section-edit-button')!.click();
        expect(sectionMocks.modalShow).toHaveBeenCalledWith(expect.objectContaining({ title: 'My section 1' }));
        const modalOptions = sectionMocks.modalShow.mock.calls[0][0] as { callback: () => void };
        modalOptions.callback();
        const input = document.getElementById('rename-section-input') as HTMLInputElement;
        expect(input.value).toBe('Old title');
        input.value = '   ';
        document.getElementById('rename-section-form')!.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }));
        await Promise.resolve();
        expect(sectionMocks.rename).not.toHaveBeenCalled();

        input.value = '  New title  ';
        document.getElementById('rename-section-form')!.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }));
        await vi.waitFor(() => expect(sectionMocks.rename).toHaveBeenCalledWith(1, 'New title'));
        expect(document.querySelector('.section-title')!.textContent).toBe(' New title');
        expect(sectionMocks.modalHide).toHaveBeenCalledOnce();
    });
});