import Csrf from "@/modules/General/Csrf";
import type { position } from '@/type/General'
import { OrganizerButtonPlaylist } from '@/modules/OrganizerButtonPlaylist'
import ConsoleCustom from "./modules/General/ConsoleCustom";
import ConsoleTesteur from "./modules/General/ConsoleTesteur";
import Time from "@/modules/Util/Time";


type DataTransfer = {
    id: string
    dragstart: string
}


document.addEventListener("DOMContentLoaded", () => {
    if (OrganizerDragAndDropZone.valid()) {
        setEventDragAndDrop()
        checkEmptyPlaylist()
        initOrderBadge()
        initAddSectionButton();
        new ScrollManager().addEvent();
    }
});

function initOrderBadge() {
    const cleanorder = new CleanOrderHandler()
    cleanorder.resetBadge()
}

class SectionConfig {
    private static _maxSections: number | null = null;

    public static getMaxSections(): number {
        this._maxSections ??= this.detectMaxSections();
        return this._maxSections;
    }

    public static refreshMaxSections(): void {
        this._maxSections = null; // Force la re-détection
    }

    private static detectMaxSections(): number {
        let sectionCount = 0;
        let sectionExists = true;
        let currentSection = 1;

        while (sectionExists && currentSection <= 10) { // Limite de sécurité à 10 sections
            const sectionEl = document.getElementById(`associated-playlists-section-${currentSection}`);
            if (sectionEl) {
                sectionCount = currentSection;
                currentSection++;
            } else {
                sectionExists = false;
            }
        }

        return Math.max(sectionCount, 1); // Au moins 1 section
    }

    public static getSectionNumbers(): number[] {
        return Array.from({ length: this.getMaxSections() }, (_, i) => i + 1);
    }

    public static getNextSectionNumber(): number {
        return this.getMaxSections() + 1;
    }
}



class OrganizerDragAndDropZone {
    public static associatedPlaylists(): HTMLDivElement {
        return document.getElementById('associated-playlists') as HTMLDivElement
    }

    public static associatedPlaylistsSection(section: number): HTMLDivElement {
        return document.getElementById(`associated-playlists-section-${section}`) as HTMLDivElement
    }

    public static getAllSections(): HTMLDivElement[] {
        return SectionConfig.getSectionNumbers().map(i => this.associatedPlaylistsSection(i)).filter(el => el !== null)
    }

    public static unassociatedPlaylists(): HTMLDivElement {
        return document.getElementById('unassociated-playlists') as HTMLDivElement
    }

    public static valid(): boolean {
        if (document.getElementById('unassociated-playlists') instanceof HTMLDivElement) {
            const sections = this.getAllSections();
            const expectedSections = SectionConfig.getMaxSections();
            return sections.length === expectedSections && expectedSections > 0;
        }
        return false;
    }

    public static getUrlFromAnySection(): string {
        const firstSection = this.associatedPlaylistsSection(1);
        return (firstSection.closest('[data-url]') as HTMLElement)?.dataset?.url || '';
    }
}

class DropPointHandler {
    playlist: HTMLElement;
    PlaylistHtmlElement: HTMLElement[];
    newOrder: number;
    insertAfter: boolean = false;
    closestElement: HTMLElement | null = null;
    constructor(playlist: HTMLElement, PlaylistHtmlElement: HTMLElement[]) {
        this.playlist = playlist.cloneNode(true) as HTMLElement;
        this.PlaylistHtmlElement = PlaylistHtmlElement;
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
        ConsoleCustom.info('this.PlaylistHtmlElement', this.PlaylistHtmlElement);



        for (const child of this.PlaylistHtmlElement) {
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
        }
    }

    async insertElement(e: DragEvent) {
        const position = this.getDropPoint(e);
        this.findClosestElement(position);
        if (this.closestElement === null || !this.playlist) return;

        const order = this.closestElement.dataset.order;
        if (!order) {
            ConsoleCustom.warn('No order found');
            return;
        }

        this.newOrder = Number.parseInt(order);


        if (this.closestElement && this.playlist) {
            if (this.insertAfter) {
                this.newOrder++;
                this.playlist.dataset.order = this.newOrder.toString();
                this.closestElement.after(this.playlist);
            } else {
                this.playlist.dataset.order = this.newOrder.toString();
                this.closestElement.before(this.playlist);
            }
            ConsoleCustom.log(`playlist inserted at order: ${this.newOrder}`);

        }
    }
}

class CleanOrderHandler {
    allSections: HTMLDivElement[];
    playlistNonAssociees: HTMLDivElement;
    constructor() {
        this.allSections = OrganizerDragAndDropZone.getAllSections();
        this.playlistNonAssociees = OrganizerDragAndDropZone.unassociatedPlaylists();
    }



    trueReorderSection(section: number) {
        ConsoleTesteur.group(`trueReorderSection called section : ${section}`);

        const sectionEl = OrganizerDragAndDropZone.associatedPlaylistsSection(section);
        const listEl = sectionEl.getElementsByClassName('playlist-dragAndDrop') as HTMLCollectionOf<HTMLDivElement>;
        let order = 1;
        for (const element of listEl) {
            if (element.dataset) {
                ConsoleTesteur.info('order:', order);

                element.dataset.order = order.toString();
                element.dataset.section = section.toString();
                order++;
            }
        }
        ConsoleTesteur.groupEnd();
        return this
    }

    trueReorder() {
        const maxSections = SectionConfig.getMaxSections();
        for (let i = 1; i <= maxSections; i++) {
            this.trueReorderSection(i);
        }
        return this
    }

    resetBadge() {

        for (const section of this.allSections) {
            if (section) { // Vérifier que la section existe
                const listEl = section.getElementsByClassName('playlist-dragAndDrop') as HTMLCollectionOf<HTMLDivElement>;
                for (const element of listEl) {
                    if (element?.id) { // Vérifier que l'élément et son ID existent
                        const buttonPlaylist = new OrganizerButtonPlaylist(element.id)
                        buttonPlaylist.removeBadge(false)
                        let order = 0;
                        if (element.dataset?.order) {
                            order = Number.parseInt(element.dataset.order)
                        }
                        buttonPlaylist.addBadge(order)
                    }
                }
            }
        }
        this.cleanUnsassociatedBadge()
        return this
    }

    cleanUnsassociatedBadge() {
        if (this.playlistNonAssociees) { // Vérifier que l'élément existe
            const listUnassociated = this.playlistNonAssociees.getElementsByClassName('playlist-dragAndDrop') as HTMLCollectionOf<HTMLDivElement>;
            for (const unassociated of listUnassociated) {
                if (unassociated?.id) { // Vérifier que l'élément et son ID existent
                    const buttonPlaylist = new OrganizerButtonPlaylist(unassociated.id)
                    buttonPlaylist.removeBadge(true)
                }
            }
        }
        return this
    }
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

    public addMusic(btnPlaylist: OrganizerButtonPlaylist, newOrder: number, section: number) {
        this.fetch('POST', {
            idPlaylist: btnPlaylist.playlist.id,
            newOrder: newOrder,
            section: section
        }, section)
    }

    public removeMusic(btnPlaylist: OrganizerButtonPlaylist) {
        this.fetch('DELETE', {
            idPlaylist: btnPlaylist.playlist.id,
        })
    }

    public updateMusic(btnPlaylist: OrganizerButtonPlaylist, newOrder: number, section: number) {
        this.fetch('UPDATE', {
            idPlaylist: btnPlaylist.playlist.id,
            newOrder: newOrder,
            section: section
        }, section)
    }

    private fetch(method: string, body: {}, section?: number) {
        ConsoleTesteur.info(`Fetch called with method: ${method}, body: ${JSON.stringify(body)}, section: ${section}`);
        const url = OrganizerDragAndDropZone.getUrlFromAnySection();
        fetch(url, {
            method: method,
            headers: {
                'X-CSRFToken': Csrf.getToken()!,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(body)
        })
            .then(response => response.json())
            .then(_data => {
                const cleanorder = new CleanOrderHandler()
                cleanorder.resetBadge()
            })
            .catch(error => ConsoleCustom.error(error));
    }

}

function setEventDragAndDrop() {
    // Sélectionner les éléments HTML
    const playlistNonAssociees = OrganizerDragAndDropZone.unassociatedPlaylists();
    const allSections = OrganizerDragAndDropZone.getAllSections();

    if (playlistNonAssociees == null || allSections.length === 0) return

    // Définir les événements de drag and drop pour chaque section
    for (const sectionEl of allSections) {
        const sectionNumber = allSections.indexOf(sectionEl) + 1;

        sectionEl.removeEventListener('dragstart', (_event: DragEvent) => { }); // clear before 
        sectionEl.addEventListener('dragstart', (e: DragEvent) => { // from associées
            const EDT = new EventDataTransfert(e)
            const target = e.target! as HTMLDivElement;
            EDT.build(target.id, `playlistAssociees-${sectionNumber}`)
        });

        sectionEl.addEventListener('dragover', (e) => {
            e.preventDefault();
        });

        sectionEl.addEventListener('drop', (elementDragged: DragEvent) => { // to associées
            ConsoleTesteur.log('drop event on associées');

            elementDragged.preventDefault();
            let orderNewElement = 0
            const EDT = EventDataTransfert.getClassFromEvent(elementDragged)
            if (EDT.DataTransfer == null) return

            const listHtmlPlaylist = [...sectionEl.getElementsByClassName('playlist-dragAndDrop')] as HTMLElement[];
            const playlist = document.getElementById(EDT.DataTransfer.id) as HTMLDivElement;

            if (!playlist) {
                ConsoleTesteur.error(`Playlist element not found with id: ${EDT.DataTransfer.id}`);
                return;
            }

            const btnPlaylist = new OrganizerButtonPlaylist(EDT.DataTransfer.id)
            const sendbackend = new SendBackendAction()

            if (EDT.DataTransfer.dragstart.startsWith('playlistAssociees')) {
                //same section 
                if (EDT.DataTransfer.dragstart === `playlistAssociees-${sectionNumber}`) {
                    ConsoleTesteur.group('Updating music in the same section', sectionEl);
                    ConsoleTesteur.log('listHtmlPlaylist', listHtmlPlaylist);

                    const handler = new DropPointHandler(playlist, listHtmlPlaylist)
                    playlist.remove();
                    handler.insertElement(elementDragged);
                    orderNewElement = handler.getNewOrder()
                    sendbackend.updateMusic(btnPlaylist, orderNewElement, sectionNumber)
                    ConsoleTesteur.groupEnd();
                } else {
                    // different section
                    ConsoleTesteur.group('Updating music in the different section', sectionEl);
                    ConsoleTesteur.log('listHtmlPlaylist', listHtmlPlaylist);

                    if (listHtmlPlaylist.length === 0) {
                        ConsoleTesteur.log('Section is empty, appending playlist directly');

                        if (sectionEl && playlist) {
                            sectionEl.appendChild(playlist);
                            orderNewElement = 1;
                        }
                    } else {
                        const handler = new DropPointHandler(playlist, listHtmlPlaylist)
                        playlist.remove();
                        handler.insertElement(elementDragged);
                        orderNewElement = handler.getNewOrder()
                    }
                    sendbackend.updateMusic(btnPlaylist, orderNewElement, sectionNumber)


                    ConsoleTesteur.groupEnd();
                }

            } else {
                ConsoleTesteur.group('Adding music from unassociated to associated');

                if (listHtmlPlaylist.length === 0) {
                    ConsoleTesteur.log('Section is empty, appending playlist directly');

                    if (sectionEl && playlist) {
                        sectionEl.appendChild(playlist);
                        orderNewElement = 1;
                    }
                } else {
                    ConsoleTesteur.log('Section is not empty, inserting playlist');
                    const handler = new DropPointHandler(playlist, listHtmlPlaylist)
                    playlist.remove();
                    handler.insertElement(elementDragged);
                    orderNewElement = handler.getNewOrder()
                }
                sendbackend.addMusic(btnPlaylist, orderNewElement, sectionNumber)
                ConsoleTesteur.groupEnd();
            }
            checkEmptyPlaylist();

            const cleanorder = new CleanOrderHandler()
            cleanorder.trueReorder().resetBadge()
        });
    };

    playlistNonAssociees.addEventListener('dragstart', (e: DragEvent) => { // from non associées
        const EDT = new EventDataTransfert(e)
        const target = e.target! as HTMLDivElement;
        EDT.build(target.id, 'playlistNonAssociees')
    });



    playlistNonAssociees.addEventListener('dragover', (e) => {
        e.preventDefault();
    });



    playlistNonAssociees.addEventListener('drop', (e: DragEvent) => { // to non associées
        ConsoleTesteur.log('drop event on non associées');

        e.preventDefault();
        const EDT = EventDataTransfert.getClassFromEvent(e)
        if (EDT.DataTransfer == null) return
        if (EDT.DataTransfer.dragstart == 'playlistNonAssociees') {
            return
        }
        const btnPlaylist = new OrganizerButtonPlaylist(EDT.DataTransfer.id)
        const id = EDT.DataTransfer.id;
        const playlist = document.getElementById(id) as HTMLElement;

        if (playlistNonAssociees && playlist) {
            playlistNonAssociees.appendChild(playlist);
        }
        checkEmptyPlaylist();
        const sendbackend = new SendBackendAction()
        sendbackend.removeMusic(btnPlaylist)

        const cleanorder = new CleanOrderHandler()
        cleanorder.trueReorder().resetBadge()
    });
}

function checkEmptyPlaylist() {
    // Vérifier chaque section
    const maxSections = SectionConfig.getMaxSections();
    for (let i = 1; i <= maxSections; i++) {
        const sectionEl = OrganizerDragAndDropZone.associatedPlaylistsSection(i);
        if (sectionEl) { // Vérifier que la section existe
            const sectionNodesElement = sectionEl.getElementsByClassName('playlist-dragAndDrop');
            const sectionEmpty = document.getElementsByClassName(`section-${i}-empty`)[0];
            if (sectionEmpty) { // Vérifier que l'élément empty existe
                if (sectionNodesElement.length == 0) {
                    sectionEmpty.removeAttribute('hidden');
                } else {
                    sectionEmpty.setAttribute('hidden', 'true');
                }
            }
        }
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

function initAddSectionButton() {
    const addSectionButton = document.getElementById('add-section-button');
    if (addSectionButton) {
        addSectionButton.addEventListener('click', () => {
            addNewSection();
        });
    }
}

function addNewSection() {
    const template = document.getElementById('add-section-template') as HTMLTemplateElement;
    if (!template) {
        ConsoleTesteur.error('Template add-section-template not found');
        return;
    }

    const nextSectionNumber = SectionConfig.getNextSectionNumber();

    // Vérifier si on dépasse la limite
    if (nextSectionNumber > Number.parseInt(template.dataset.maxSection!)) {
        ConsoleTesteur.warn(`Maximum number of sections reached (${template.dataset.maxSection})`);
        return;
    }

    // Cloner le template
    const clone = template.content.cloneNode(true) as DocumentFragment;

    // Mettre à jour les IDs et numéros de section
    const sectionContainer = clone.querySelector('.section-container') as HTMLDivElement;
    const sectionEmpty = clone.querySelector('[class*="section-"][class*="-empty"]') as HTMLSpanElement;
    const numSectionSpan = clone.querySelector('.num-section') as HTMLSpanElement;

    if (sectionContainer && sectionEmpty && numSectionSpan) {
        // Mettre à jour l'ID et les attributs
        sectionContainer.id = `associated-playlists-section-${nextSectionNumber}`;
        sectionContainer.dataset.section = nextSectionNumber.toString();

        // Mettre à jour les classes et numéros
        sectionEmpty.className = sectionEmpty.className.replace(
            /section-\d+-empty/,
            `section-${nextSectionNumber}-empty`
        );
        numSectionSpan.textContent = nextSectionNumber.toString();

        // Trouver le conteneur parent pour insérer la nouvelle section
        const parentContainer = document.getElementById('associated-playlists-container');
        if (parentContainer) {
            parentContainer.appendChild(clone);

            // Rafraîchir la configuration des sections
            SectionConfig.refreshMaxSections();

            ConsoleTesteur.info(`Section ${nextSectionNumber} added successfully`);

            setEventDragAndDrop();
        }
    }
}

class ScrollManager {
    private scrollInterval: number | null = null;
    private scrollSpeed: number; // pixels per interval
    private scrollZone: number; // pixels from edge to trigger scroll

    constructor() {
        this.scrollZone = window.innerHeight * 0.15;
        this.scrollSpeed = window.innerHeight * 0.30;
    }

    public addEvent() {
        // Add dragover event to document to handle auto-scroll
        document.addEventListener('dragover', (e) => {
            e.preventDefault();

            const mouseY = e.clientY;
            const windowHeight = window.innerHeight;

            console.log(`mouseY: ${mouseY}, windowHeight: ${windowHeight}, scrollZone: ${this.scrollZone}`);


            if (mouseY < this.scrollZone) {
                // Near top edge
                this.startAutoScroll('up');
            } else if (mouseY > windowHeight - this.scrollZone) {
                // Near bottom edge
                this.startAutoScroll('down');
            } else {
                // In middle area
                this.stopAutoScroll();
            }
        });
        // Stop scrolling when drag leaves the window
        document.addEventListener('dragleave', (_) => {
            this.stopAutoScroll();
        });

        document.addEventListener('dragdrop', (_) => {
            this.stopAutoScroll();
        });


    }

    private detectTop(): boolean {
        return window.scrollY === 0;
    }

    private detectBottom(): boolean {
        return (window.innerHeight + window.scrollY) >= document.body.offsetHeight;
    }

    private startAutoScroll(direction: 'up' | 'down') {
        if (this.scrollInterval) return;
        this.scrollInterval = setInterval(() => {
            console.log(`Auto-scrolling ${direction}`);

            if (direction === 'up') {
                window.scrollBy(0, -this.scrollSpeed);
                if (this.detectTop()) {
                    this.stopAutoScroll();
                }
            } else { //down
                window.scrollBy(0, this.scrollSpeed);
                if (this.detectBottom()) {
                    this.stopAutoScroll();
                }
            }
        }, 16);
    }

    private stopAutoScroll() {
        if (this.scrollInterval) {
            clearInterval(this.scrollInterval);
            this.scrollInterval = null;
        }
    }



}




