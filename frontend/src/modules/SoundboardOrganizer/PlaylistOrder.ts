import { OrganizerDragAndDropZone, SectionConfig } from './OrganizerDom';
import ConsoleTesteur from '@/modules/General/ConsoleTesteur';

export class PlaylistOrderNormalizer {
    public normalizeSection(sectionNumber: number): void {
        const section = OrganizerDragAndDropZone.associatedPlaylistsSection(sectionNumber);
        const playlists = section.getElementsByClassName('playlist-dragAndDrop') as HTMLCollectionOf<HTMLDivElement>;
        let order = 1;
        for (const playlist of playlists) {
            playlist.dataset.order = (order++).toString();
            playlist.dataset.section = sectionNumber.toString();
        }
        ConsoleTesteur.info('Reordered section:', sectionNumber);
    }

    public normalizeAll(): void {
        for (const sectionNumber of SectionConfig.getSectionNumbers()) {
            this.normalizeSection(sectionNumber);
        }
    }
}
