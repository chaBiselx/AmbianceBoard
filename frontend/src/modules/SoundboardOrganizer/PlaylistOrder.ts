import { OrganizerButtonPlaylist } from '@/modules/OrganizerButtonPlaylist';
import { OrganizerDragAndDropZone, SectionConfig } from './OrganizerDom';
import ConsoleTesteur from '@/modules/General/ConsoleTesteur';

class BadgeRenderer {
    public refreshSectionBadges(sections: HTMLDivElement[]): void {
        for (const section of sections) {
            const playlists = section.getElementsByClassName('playlist-dragAndDrop') as HTMLCollectionOf<HTMLDivElement>;
            for (const playlist of playlists) {
                if (!playlist.id) continue;
                const button = new OrganizerButtonPlaylist(playlist.id);
                button.removeBadge(false);
                button.addBadge(Number.parseInt(playlist.dataset.order || '0'));
            }
        }
    }

    public clearUnassociatedBadges(unassociatedPlaylists: HTMLDivElement): void {
        const playlists = unassociatedPlaylists.getElementsByClassName('playlist-dragAndDrop') as HTMLCollectionOf<HTMLDivElement>;
        for (const playlist of playlists) {
            if (playlist.id) new OrganizerButtonPlaylist(playlist.id).removeBadge(true);
        }
    }
}

export class CleanOrderHandler {
    private readonly allSections: HTMLDivElement[];
    private readonly unassociatedPlaylists: HTMLDivElement;
    private readonly badgeRenderer = new BadgeRenderer();

    constructor() {
        this.allSections = OrganizerDragAndDropZone.getAllSections();
        this.unassociatedPlaylists = OrganizerDragAndDropZone.unassociatedPlaylists();
    }

    public trueReorderSection(sectionNumber: number): this {
        const section = OrganizerDragAndDropZone.associatedPlaylistsSection(sectionNumber);
        const playlists = section.getElementsByClassName('playlist-dragAndDrop') as HTMLCollectionOf<HTMLDivElement>;
        let order = 1;
        for (const playlist of playlists) {
            playlist.dataset.order = (order++).toString();
            playlist.dataset.section = sectionNumber.toString();
        }
        ConsoleTesteur.info('Reordered section:', sectionNumber);
        return this;
    }

    public trueReorder(): this {
        for (const sectionNumber of SectionConfig.getSectionNumbers()) {
            this.trueReorderSection(sectionNumber);
        }
        return this;
    }

    public resetBadge(): this {
        this.badgeRenderer.refreshSectionBadges(this.allSections);
        this.cleanUnsassociatedBadge();
        return this;
    }

    public cleanUnsassociatedBadge(): this {
        this.badgeRenderer.clearUnassociatedBadges(this.unassociatedPlaylists);
        return this;
    }
}