/** DOM helpers for the soundboard playlist organizer. */
export class SectionConfig {
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

        while (currentSection <= 10) {
            if (!document.getElementById(`associated-playlists-section-${currentSection}`)) {
                break;
            }
            sectionCount = currentSection++;
        }

        return Math.max(sectionCount, 1);
    }

    public static getSectionNumbers(): number[] {
        return Array.from({ length: this.getMaxSections() }, (_, index) => index + 1);
    }

    public static getNextSectionNumber(): number {
        return this.getMaxSections() + 1;
    }
}

export class OrganizerDragAndDropZone {
    public static associatedPlaylists(): HTMLDivElement {
        return document.getElementById('associated-playlists') as HTMLDivElement;
    }

    public static associatedPlaylistsSection(section: number): HTMLDivElement {
        return document.getElementById(`associated-playlists-section-${section}`) as HTMLDivElement;
    }

    public static getAllSections(): HTMLDivElement[] {
        return SectionConfig.getSectionNumbers()
            .map(section => this.associatedPlaylistsSection(section))
            .filter((element): element is HTMLDivElement => element !== null);
    }

    public static unassociatedPlaylists(): HTMLDivElement {
        return document.getElementById('unassociated-playlists') as HTMLDivElement;
    }

    public static valid(): boolean {
        if (!(document.getElementById('unassociated-playlists') instanceof HTMLDivElement)) {
            return false;
        }
        const expectedSections = SectionConfig.getMaxSections();
        return this.getAllSections().length === expectedSections && expectedSections > 0;
    }

    public static getUrlFromAnySection(): string {
        const firstSection = this.associatedPlaylistsSection(1);
        return (firstSection.closest('[data-url]') as HTMLElement)?.dataset.url || '';
    }
}

export class EmptyPlaylistChecker {
    public static check(): void {
        for (const section of SectionConfig.getSectionNumbers()) {
            const sectionElement = OrganizerDragAndDropZone.associatedPlaylistsSection(section);
            const emptyMessage = document.getElementsByClassName(`section-${section}-empty`)[0];
            if (sectionElement && emptyMessage) {
                emptyMessage.toggleAttribute('hidden', sectionElement.getElementsByClassName('playlist-dragAndDrop').length > 0);
            }
        }

        const unassociatedPlaylists = OrganizerDragAndDropZone.unassociatedPlaylists();
        const emptyMessage = document.getElementsByClassName('unassociated-playlists-empty')[0];
        if (unassociatedPlaylists && emptyMessage) {
            emptyMessage.toggleAttribute('hidden', unassociatedPlaylists.getElementsByClassName('playlist-dragAndDrop').length > 0);
        }
    }
}