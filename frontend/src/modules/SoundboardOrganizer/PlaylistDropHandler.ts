import type { position } from '@/type/General';
import { OrganizerButtonPlaylist } from '@/modules/OrganizerButtonPlaylist';
import ConsoleCustom from '@/modules/General/ConsoleCustom';
import ConsoleTesteur from '@/modules/General/ConsoleTesteur';
import { EmptyPlaylistChecker } from './OrganizerDom';
import { SendBackendAction } from './OrganizerApi';
import { CleanOrderHandler } from './PlaylistOrder';

type DragInfo = {
    id: string;
    dragstart: string;
};

class DropPointHandler {
    private readonly playlist: HTMLElement;
    private readonly playlists: HTMLElement[];
    private newOrder = 0;
    private insertAfter = false;
    private closestElement: HTMLElement | null = null;

    constructor(playlist: HTMLElement, playlists: HTMLElement[]) {
        this.playlist = playlist.cloneNode(true) as HTMLElement;
        this.playlists = playlists;
    }

    public getNewOrder(): number {
        return this.newOrder;
    }

    public insertElement(event: PointerEvent): void {
        this.findClosestElement({ x: event.clientX, y: event.clientY });
        if (!this.closestElement) return;

        const order = this.closestElement.dataset.order;
        if (!order) {
            ConsoleCustom.warn('No order found');
            return;
        }

        this.newOrder = Number.parseInt(order);
        if (this.insertAfter) {
            this.newOrder++;
            this.playlist.dataset.order = this.newOrder.toString();
            this.closestElement.after(this.playlist);
        } else {
            this.playlist.dataset.order = this.newOrder.toString();
            this.closestElement.before(this.playlist);
        }
    }

    private findClosestElement(dropPoint: position): void {
        let closestDistance = Infinity;

        for (const child of this.playlists) {
            const rect = child.getBoundingClientRect();
            const center = { x: rect.left + rect.width / 2, y: rect.top + rect.height / 2 };
            const distance = Math.hypot(dropPoint.x - center.x, dropPoint.y - center.y);

            if (distance < closestDistance) {
                closestDistance = distance;
                this.closestElement = child;
                this.insertAfter = Math.abs(dropPoint.y - center.y) < rect.height / 2
                    ? dropPoint.x > center.x
                    : dropPoint.y > center.y;
            }
        }
    }
}

export class PlaylistDropHandler {
    public handleSectionDrop(event: PointerEvent, section: HTMLDivElement, sectionNumber: number, dragInfo: DragInfo): void {
        const playlist = document.getElementById(dragInfo.id) as HTMLDivElement | null;
        if (!playlist) {
            ConsoleTesteur.error(`Playlist element not found with id: ${dragInfo.id}`);
            return;
        }

        const playlists = [...section.getElementsByClassName('playlist-dragAndDrop')] as HTMLElement[];
        const fromSection = dragInfo.dragstart.startsWith('playlistAssociees');
        const sameSection = dragInfo.dragstart === `playlistAssociees-${sectionNumber}`;
        const order = this.insertPlaylist(event, playlist, playlists, section, sameSection);
        const backend = new SendBackendAction();
        const button = new OrganizerButtonPlaylist(dragInfo.id);

        if (order > 0) {
            fromSection ? backend.updateMusic(button, order, sectionNumber) : backend.addMusic(button, order, sectionNumber);
        }
        EmptyPlaylistChecker.check();
        new CleanOrderHandler().trueReorder().resetBadge();
    }

    public handleUnassociatedDrop(_: PointerEvent, unassociatedPlaylists: HTMLDivElement, dragInfo: DragInfo): void {
        if (dragInfo.dragstart === 'playlistNonAssociees') return;

        const playlist = document.getElementById(dragInfo.id) as HTMLElement | null;
        if (!playlist) {
            ConsoleTesteur.error(`Playlist element not found with id: ${dragInfo.id}`);
            return;
        }

        unassociatedPlaylists.appendChild(playlist);
        EmptyPlaylistChecker.check();
        new SendBackendAction().removeMusic(new OrganizerButtonPlaylist(dragInfo.id), Number.parseInt(playlist.dataset.section || '0'));
        new CleanOrderHandler().trueReorder().resetBadge();
    }

    private insertPlaylist(event: PointerEvent, playlist: HTMLDivElement, playlists: HTMLElement[], section: HTMLDivElement, sameSection: boolean): number {
        if (sameSection && playlists.length === 1) return 0;
        if (playlists.length === 0) {
            section.appendChild(playlist);
            return 1;
        }

        const handler = new DropPointHandler(playlist, playlists);
        playlist.remove();
        handler.insertElement(event);
        return handler.getNewOrder();
    }
}

export type { DragInfo };