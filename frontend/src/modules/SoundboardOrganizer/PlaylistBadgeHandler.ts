import { OrganizerButtonPlaylist } from '@/modules/OrganizerButtonPlaylist';
import { OrganizerDragAndDropZone } from './OrganizerDom';

export class PlaylistBadgeHandler {
    private readonly sections: HTMLDivElement[];
    private readonly unassociatedPlaylists: HTMLDivElement;
    private readonly playlistClassName = 'playlist-dragAndDrop';

    constructor() {
        this.sections = OrganizerDragAndDropZone.getAllSections();
        this.unassociatedPlaylists = OrganizerDragAndDropZone.unassociatedPlaylists();
    }

    public refresh(): void {
        this.refreshSectionBadges();
        this.clearUnassociatedBadges();
    }

    private refreshSectionBadges(): void {
        for (const section of this.sections) {
            const playlists = section.getElementsByClassName(this.playlistClassName) as HTMLCollectionOf<HTMLDivElement>;
            for (const playlist of playlists) {
                if (!playlist.id) continue;
                const button = new OrganizerButtonPlaylist(playlist.id);
                button.removeBadge(false);
                button.addBadge(Number.parseInt(playlist.dataset.order || '0'));
            }
        }
    }

    private clearUnassociatedBadges(): void {
        const playlists = this.unassociatedPlaylists.getElementsByClassName(this.playlistClassName) as HTMLCollectionOf<HTMLDivElement>;
        for (const playlist of playlists) {
            if (playlist.id) new OrganizerButtonPlaylist(playlist.id).removeBadge(true);
        }
    }
}
