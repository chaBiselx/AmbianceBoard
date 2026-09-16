import ConsoleCustom from '@/modules/General/ConsoleCustom';
import ConsoleTesteur from '@/modules/General/ConsoleTesteur';
import { SendBackendAction } from './OrganizerApi';
import { EmptyPlaylistChecker, OrganizerDragAndDropZone, SectionConfig } from './OrganizerDom';
import { CleanOrderHandler } from './PlaylistOrder';

class SectionDomManager {
    public updateAccordionNode(accordionNode: HTMLElement, sectionNumber: number): void {
        const sectionContainer = accordionNode.querySelector('.section-container') as HTMLDivElement;
        accordionNode.querySelector('.num-section')!.textContent = sectionNumber.toString();
        sectionContainer.id = `associated-playlists-section-${sectionNumber}`;
        sectionContainer.dataset.section = sectionNumber.toString();
        for (const playlist of sectionContainer.getElementsByClassName('playlist-dragAndDrop') as HTMLCollectionOf<HTMLDivElement>) {
            playlist.dataset.section = sectionNumber.toString();
        }
        const emptyMessage = accordionNode.querySelector('[class*="section-"][class*="-empty"]') as HTMLSpanElement | null;
        if (emptyMessage) emptyMessage.className = emptyMessage.className.replace(/section-\d+-empty/, `section-${sectionNumber}-empty`);
        const header = accordionNode.querySelector('.accordion-header') as HTMLHeadingElement;
        header.id = `panelsSection-${sectionNumber}`;
        const button = accordionNode.querySelector('.accordion-button') as HTMLButtonElement;
        button.setAttribute('aria-controls', `panelsStayOpen-${sectionNumber}`);
        button.dataset.bsTarget = `#panelsStayOpen-${sectionNumber}`;
        const collapse = accordionNode.querySelector('.accordion-collapse') as HTMLDivElement;
        collapse.id = `panelsStayOpen-${sectionNumber}`;
        collapse.setAttribute('aria-labelledby', `panelsSection-${sectionNumber}`);
        const insertButton = accordionNode.querySelector('.section-insert-before-button') as HTMLButtonElement | null;
        if (insertButton) insertButton.dataset.numSection = sectionNumber.toString();
        const deleteButton = accordionNode.querySelector('.section-delete-button') as HTMLButtonElement | null;
        if (deleteButton) deleteButton.dataset.numSection = sectionNumber.toString();
    }

    public buildSectionNode(template: HTMLTemplateElement, sectionNumber: number): HTMLElement | null {
        const accordionNode = (template.content.cloneNode(true) as DocumentFragment).querySelector('.accordion') as HTMLElement | null;
        if (!accordionNode) return null;
        this.updateAccordionNode(accordionNode, sectionNumber);
        return accordionNode;
    }

    public shiftSectionsForInsertion(insertPosition: number): void {
        for (let sectionNumber = SectionConfig.getMaxSections(); sectionNumber >= insertPosition; sectionNumber--) {
            const accordionNode = OrganizerDragAndDropZone.associatedPlaylistsSection(sectionNumber)?.closest('.accordion') as HTMLElement | null;
            if (!accordionNode) continue;
            const shiftedNode = accordionNode.cloneNode(true) as HTMLElement;
            this.updateAccordionNode(shiftedNode, sectionNumber + 1);
            accordionNode.replaceWith(shiftedNode);
        }
    }

    public shiftSectionsForDeletion(deletedSection: number, maxSection: number): void {
        for (let sectionNumber = deletedSection + 1; sectionNumber <= maxSection; sectionNumber++) {
            const accordionNode = OrganizerDragAndDropZone.associatedPlaylistsSection(sectionNumber)?.closest('.accordion') as HTMLElement | null;
            if (!accordionNode) continue;
            const shiftedNode = accordionNode.cloneNode(true) as HTMLElement;
            this.updateAccordionNode(shiftedNode, sectionNumber - 1);
            accordionNode.replaceWith(shiftedNode);
        }
    }
}

class SectionAdder {
    private readonly template: HTMLTemplateElement | null = null;
    private readonly sectionDomManager = new SectionDomManager();

    constructor(private readonly setupDragEvents: () => void) {
        this.template = document.getElementById('add-section-template') as HTMLTemplateElement | null;
        if (!this.template) ConsoleTesteur.error('Template add-section-template not found');
    }

    public addEvent(): void {
        document.getElementById('add-section-button')?.addEventListener('click', () => {
            SectionConfig.refreshMaxSections();
            void this.addSectionAt(SectionConfig.getNextSectionNumber());
        });
        const parent = document.getElementById('associated-playlists-container');
        if (parent && !parent.dataset.insertSectionBound) {
            parent.addEventListener('click', event => {
                const position = Number.parseInt((event.target as HTMLElement).closest<HTMLButtonElement>('.section-insert-before-button')?.dataset.numSection || '');
                if (position > 0) void this.addSectionAt(position);
            });
            parent.dataset.insertSectionBound = 'true';
        }
    }

    private async addSectionAt(insertPosition: number): Promise<void> {
        try {
            if (!this.template) return;
            SectionConfig.refreshMaxSections();
            const currentCount = SectionConfig.getMaxSections();
            const nextSection = currentCount + 1;
            const position = Math.max(1, Math.min(insertPosition, nextSection));
            if (nextSection > Number.parseInt(this.template.dataset.maxSection || '0')) return;
            const shiftExistingSections = position <= currentCount;
            if (!await new SendBackendAction().insertSection(position)) return;
            const parent = document.getElementById('associated-playlists-container');
            if (!parent) return;
            if (shiftExistingSections) this.sectionDomManager.shiftSectionsForInsertion(position);
            const node = this.sectionDomManager.buildSectionNode(this.template, position);
            if (!node) return;
            const anchor = shiftExistingSections
                ? OrganizerDragAndDropZone.associatedPlaylistsSection(position + 1)?.closest('.accordion')
                : null;
            anchor?.parentElement === parent ? anchor.before(node) : parent.appendChild(node);
            SectionConfig.refreshMaxSections();
            this.setupDragEvents();
            EmptyPlaylistChecker.check();
            new CleanOrderHandler().resetBadge();
        } catch (error) {
            ConsoleCustom.error('Failed to insert section', error);
        }
    }
}

class SectionDeleter {
    private readonly sectionDomManager = new SectionDomManager();

    constructor(private readonly setupDragEvents: () => void) {}

    public addEvent(): void {
        const parent = document.getElementById('associated-playlists-container');
        if (parent && !parent.dataset.deleteSectionBound) {
            parent.addEventListener('click', event => {
                const position = Number.parseInt((event.target as HTMLElement).closest<HTMLButtonElement>('.section-delete-button')?.dataset.numSection || '');
                if (position > 0) void this.deleteSectionAt(position);
            });
            parent.dataset.deleteSectionBound = 'true';
        }
    }

    private async deleteSectionAt(section: number): Promise<void> {
        try {
            SectionConfig.refreshMaxSections();
            const currentCount = SectionConfig.getMaxSections();
            if (currentCount <= 1) return;
            if (!confirm('Supprimer cette section et tous ses boutons associés ?')) return;
            if (!await new SendBackendAction().deleteSection(section)) return;

            const accordionNode = OrganizerDragAndDropZone.associatedPlaylistsSection(section)?.closest('.accordion') as HTMLElement | null;
            accordionNode?.remove();
            this.sectionDomManager.shiftSectionsForDeletion(section, currentCount);

            SectionConfig.refreshMaxSections();
            this.setupDragEvents();
            EmptyPlaylistChecker.check();
            new CleanOrderHandler().resetBadge();
        } catch (error) {
            ConsoleCustom.error('Failed to delete section', error);
        }
    }
}

export { SectionAdder, SectionDeleter };