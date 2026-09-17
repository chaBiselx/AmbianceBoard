import ConsoleCustom from '@/modules/General/ConsoleCustom';
import { SendBackendAction } from './OrganizerApi';

/** Détecte le nombre de sections déjà présentes sur la page du soundboard (mode lecture/édition). */
class BoardSectionConfig {
    private static maxSections: number | null = null;

    public static getMaxSections(): number {
        this.maxSections ??= this.detectMaxSections();
        return this.maxSections;
    }

    public static refreshMaxSections(): void {
        this.maxSections = null;
    }

    private static detectMaxSections(): number {
        let sectionCount = 0;
        let currentSection = 1;

        while (document.getElementById(`board-section-${currentSection}`)) {
            sectionCount = currentSection++;
        }

        return Math.max(sectionCount, 1);
    }
}

/** Permet d'ajouter une section vide en fin de soundboard depuis la page de lecture, en mode édition. */
export class BoardSectionAdder {
    private readonly template: HTMLTemplateElement | null = null;
    private readonly container: HTMLElement | null = null;

    constructor(private readonly onSectionAdded: (node: HTMLElement) => void) {
        this.template = document.getElementById('add-board-section-template') as HTMLTemplateElement | null;
        this.container = document.querySelector('[data-soundboard-organize-uri]');
    }

    public addEvent(): void {
        document.getElementById('soundboard-add-section-button')?.addEventListener('click', () => {
            void this.addSection();
        });
    }

    private buildSectionNode(sectionNumber: number): HTMLElement | null {
        if (!this.template) return null;
        const section = (this.template.content.cloneNode(true) as DocumentFragment).querySelector('section') as HTMLElement | null;
        if (!section) return null;
        section.id = `board-section-${sectionNumber}`;
        section.className = section.className.replace('section-0', `section-${sectionNumber}`);
        // A Title for the section
        const sectionHeader = section.getElementsByClassName('section-header');
        if ( sectionHeader?.length > 0) {
            sectionHeader[0].textContent = `Section ${sectionNumber}`;
        }
        const addZone = section.querySelector('.soundboard-edit-add-zone') as HTMLElement | null;
        if (addZone) addZone.dataset.section = sectionNumber.toString();
        return section;
    }

    private async addSection(): Promise<void> {
        try {
            if (!this.template || !this.container) return;
            const url = this.container.dataset.soundboardOrganizeUri;
            if (!url) return;

            BoardSectionConfig.refreshMaxSections();
            const nextSection = BoardSectionConfig.getMaxSections() + 1;
            const maxAllowed = Number.parseInt(this.template.dataset.maxSection || '0');
            if (maxAllowed > 0 && nextSection > maxAllowed) return;

            if (!await new SendBackendAction().insertSection(nextSection, url)) return;

            const node = this.buildSectionNode(nextSection);
            if (!node) return;
            this.container.appendChild(node);
            BoardSectionConfig.refreshMaxSections();
            this.onSectionAdded(node);
        } catch (error) {
            ConsoleCustom.error('Failed to insert board section', error);
        }
    }
}
