import Cookie from "@/modules/Cookie";
import type { position } from '@/type/General'
import { OrganizerButtonPlaylist } from '@/modules/OrganizerButtonPlaylist'

document.addEventListener("DOMContentLoaded", () => {
    if (OrganizerDragAndDropZone.valid()) {
        setEventDragAndDrop()
        checkEmptyPlaylist()
        initOrderBadge()
    }
});





class OrganizerDragAndDropZone {
    public static associatedPlaylists(): HTMLDivElement {
        return document.getElementById('associated-playlists') as HTMLDivElement
    }

    public static unassociatedPlaylists(): HTMLDivElement {
        return document.getElementById('unassociated-playlists') as HTMLDivElement
    }

    public static valid(): boolean {
        if (document.getElementById('unassociated-playlists') instanceof HTMLDivElement && document.getElementById('associated-playlists') instanceof HTMLDivElement) {
            return true;
        }
        return false;

    }
}

class DropPointHandler {
    playlist: HTMLElement;
    children: HTMLElement[];
    newOrder: number;
    insertAfter: boolean = false;
    closestElement: HTMLElement | null = null;
    constructor(playlist: HTMLElement, children: HTMLElement[]) {
        this.playlist = playlist;
        this.children = children;
        this.newOrder = 0;
    }

    getDropPoint(e: DragEvent): position {
        return {
            x: e.clientX,
            y: e.clientY
        };
    }

    getNewOrder(): number {
        return this.newOrder;
    }

    findClosestElement(dropPoint: position) {
        let closestDistance = Infinity;

        this.children.forEach((child) => {
            if (child === this.playlist) return;

            const rect = child.getBoundingClientRect();
            const childCenter = {
                x: rect.left + rect.width / 2,
                y: rect.top + rect.height / 2
            } as position;

            const distance = Math.sqrt(
                Math.pow(dropPoint.x - childCenter.x, 2) +
                Math.pow(dropPoint.y - childCenter.y, 2)
            );

            if (distance < closestDistance) {
                closestDistance = distance;
                this.closestElement = child;

                if (Math.abs(dropPoint.y - childCenter.y) < rect.height / 2) {
                    this.insertAfter = dropPoint.x > childCenter.x;
                } else {
                    this.insertAfter = dropPoint.y > childCenter.y;
                }
            }
        });
    }

    insertElement(e: DragEvent) {
        const position = this.getDropPoint(e);
        this.findClosestElement(position);
        if (this.closestElement === null) return
        this.newOrder = parseInt(this.closestElement.dataset.order!);

        if (this.closestElement) {
            if (this.insertAfter) {
                this.newOrder++;
                this.playlist.dataset.order = this.newOrder.toString();
                this.closestElement.after(this.playlist);
            } else {
                this.playlist.dataset.order = this.newOrder.toString();
                this.closestElement.before(this.playlist);
            }
        }
    }
}

class CleanOrderHandler {
    associatedPlaylists: HTMLDivElement;
    playlistNonAssociees: HTMLDivElement;
    constructor() {
        this.associatedPlaylists = OrganizerDragAndDropZone.associatedPlaylists();
        this.playlistNonAssociees = OrganizerDragAndDropZone.unassociatedPlaylists();
    }

    getAssociatedPlaylists() {
        return this.associatedPlaylists
    }

    reorderFrom(order = 0) {
        const listEl = this.associatedPlaylists.getElementsByClassName('playlist-dragAndDrop') as HTMLCollectionOf<HTMLDivElement>;
        for (let i = 1; i <= listEl.length; i++) {
            if (i + 1 >= order && order > 1) {
                if (listEl[i].dataset) {
                    listEl[i].dataset.order = (parseInt(listEl[i].dataset.order as string) + 1).toString()
                }
            }
        }
        return this
    }

    trueReorder() {
        const listEl = this.associatedPlaylists.getElementsByClassName('playlist-dragAndDrop') as HTMLCollectionOf<HTMLDivElement>;
        let order = 1;
        for (const element of listEl) {
            if(element.dataset){
                element.dataset.order = order.toString();
                order++;
            }
        }
        return this
    }

    resetBadge() {
        const listEl = this.associatedPlaylists.getElementsByClassName('playlist-dragAndDrop') as HTMLCollectionOf<HTMLDivElement>;
        for (const element of listEl) {
            const buttonPlaylist = new OrganizerButtonPlaylist(element.id)
            buttonPlaylist.removeBadge(false)
            let order = 0;
            if (element.dataset) {
                order = parseInt(element.dataset.order!)
            }
            buttonPlaylist.addBadge(order) 
        }
        this.cleanUnsassociatedBadge()

        return this
    }

    cleanUnsassociatedBadge() {
        const listUnassociated = this.playlistNonAssociees.getElementsByClassName('playlist-dragAndDrop') as HTMLCollectionOf<HTMLDivElement>;
        for (const unassociated of listUnassociated) {
            const buttonPlaylist = new OrganizerButtonPlaylist(unassociated.id)
            buttonPlaylist.removeBadge(true)
        }
        return this
    }
}

type DataTransfer = {
    id: string
    dragstart: string
}
class EventDataTransfert {
    event: DragEvent;
    DataTransfer: DataTransfer | null = null;
    constructor(event: DragEvent) {
        this.event = event;
    }

    public setDataTransfer(dataTransfer: DataTransfer) {
        this.DataTransfer = dataTransfer
    }

    public build(id: string, dragstart: string) {
        this.DataTransfer = {
            id: id,
            dragstart: dragstart
        }
        this.event.dataTransfer!.setData('id', id);
        this.event.dataTransfer!.setData('dragstart', dragstart);
    }

    public static getClassFromEvent(event: DragEvent): EventDataTransfert {
        const dataTransfer = event.dataTransfer!
        let DT = {
            id: dataTransfer.getData('id'),
            dragstart: dataTransfer.getData('dragstart'),
        } as DataTransfer;
        const EDT = new EventDataTransfert(event);
        EDT.setDataTransfer(DT);
        return EDT;
    }
}


class SendBackendAction {

    public addMusic(btnPlaylist: OrganizerButtonPlaylist, newOrder: number) {
        this.fetch('POST', {
            idPlaylist: btnPlaylist.playlist.id,
            newOrder: newOrder
        })
    }

    public removeMusic(btnPlaylist: OrganizerButtonPlaylist) {
        this.fetch('DELETE', {
            idPlaylist: btnPlaylist.playlist.id,
        })
    }

    public updateMusic(btnPlaylist: OrganizerButtonPlaylist, newOrder: number) {
        this.fetch('UPDATE', {
            idPlaylist: btnPlaylist.playlist.id,
            newOrder: newOrder
        })
    }

    private fetch(method: string, body: {}) {
        const associatedPlaylists = OrganizerDragAndDropZone.associatedPlaylists();
        const url = associatedPlaylists.dataset.url as string;
        const csrfToken = Cookie.get('csrftoken')!;
        fetch(url, {
            method: method,
            headers: {
                'X-CSRFToken': csrfToken,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(body)
        })
            .then(response => response.json())
            .then(data => {
                const cleanorder = new CleanOrderHandler()
                cleanorder.reorderFrom(data.order).resetBadge()
            })
            .catch(error => console.error(error));
    }

}


function initOrderBadge() {
    const cleanorder = new CleanOrderHandler()
    cleanorder.resetBadge()
}

function setEventDragAndDrop() {
    // Sélectionner les éléments HTML
    const playlistNonAssociees = OrganizerDragAndDropZone.unassociatedPlaylists();
    const playlistAssociees = OrganizerDragAndDropZone.associatedPlaylists();

    if (playlistNonAssociees == null || playlistAssociees == null) return

    // Définir les événements de drag and drop
    playlistAssociees.addEventListener('dragstart', (e: DragEvent) => { // from associées
        const EDT = new EventDataTransfert(e)
        const target = e.target! as HTMLDivElement;
        EDT.build(target.id, 'playlistAssociees')
    });

    playlistNonAssociees.addEventListener('dragstart', (e: DragEvent) => { // from non associées
        const EDT = new EventDataTransfert(e)
        const target = e.target! as HTMLDivElement;
        EDT.build(target.id, 'playlistNonAssociees')
    });

    playlistAssociees.addEventListener('dragover', (e) => {
        e.preventDefault();
    });

    playlistNonAssociees.addEventListener('dragover', (e) => {
        e.preventDefault();
    });

    playlistAssociees.addEventListener('drop', (e: DragEvent) => { // to associées
        e.preventDefault();
        let orderNewElement = 0
        const EDT = EventDataTransfert.getClassFromEvent(e)
        if (EDT.DataTransfer == null) return

        const children = [...playlistAssociees.children] as HTMLElement[];
        const playlist = document.getElementById(EDT.DataTransfer.id) as HTMLDivElement;
        const btnPlaylist = new OrganizerButtonPlaylist(EDT.DataTransfer.id)
        const sendbackend = new SendBackendAction()
        if (EDT.DataTransfer.dragstart == 'playlistAssociees') {

            const handler = new DropPointHandler(playlist, children)
            playlist.remove();
            handler.insertElement(e)
            orderNewElement = handler.getNewOrder()
            sendbackend.updateMusic(btnPlaylist, orderNewElement)

        } else {
            if (children.length === 0) {
                playlistAssociees.appendChild(playlist);
            } else {
                const handler = new DropPointHandler(playlist, children)
                handler.insertElement(e)
                orderNewElement = handler.getNewOrder()
            }
            sendbackend.addMusic(btnPlaylist, orderNewElement)
        }
        checkEmptyPlaylist();

        const cleanorder = new CleanOrderHandler()
        cleanorder.trueReorder().resetBadge()

    });

    playlistNonAssociees.addEventListener('drop', (e: DragEvent) => { // to non associées
        e.preventDefault();
        const EDT = EventDataTransfert.getClassFromEvent(e)
        if (EDT.DataTransfer == null) return
        if (EDT.DataTransfer.dragstart == 'playlistNonAssociees') {
            return
        }
        const btnPlaylist = new OrganizerButtonPlaylist(EDT.DataTransfer.id)
        const id = EDT.DataTransfer.id;
        const playlist = document.getElementById(id) as HTMLElement;
        playlistNonAssociees.appendChild(playlist);
        checkEmptyPlaylist();
        const sendbackend = new SendBackendAction()
        sendbackend.removeMusic(btnPlaylist)
    });
}

function checkEmptyPlaylist() {
    const associatedPlaylists = OrganizerDragAndDropZone.associatedPlaylists();
    const associatedNodesElement = associatedPlaylists.getElementsByClassName('playlist-dragAndDrop');
    const associatedPlaylistsEmpty = document.getElementsByClassName('associated-playlists-empty')[0];
    if (associatedNodesElement.length == 0) {
        associatedPlaylistsEmpty.removeAttribute('hidden');
    } else {
        associatedPlaylistsEmpty.setAttribute('hidden', 'true');
    }

    const unassociatedPlaylists = OrganizerDragAndDropZone.unassociatedPlaylists();
    const unassociatedNodesElement = unassociatedPlaylists.getElementsByClassName('playlist-dragAndDrop');
    const unassociatedPlaylistsEmpty = document.getElementsByClassName('unassociated-playlists-empty')[0];
    if (unassociatedNodesElement.length == 0) {
        unassociatedPlaylistsEmpty.removeAttribute('hidden');
    } else {
        unassociatedPlaylistsEmpty.setAttribute('hidden', 'true');
    }
}



