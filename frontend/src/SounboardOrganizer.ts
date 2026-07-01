import Csrf from "@/modules/General/Csrf";
import type { position } from '@/type/General'
import { OrganizerButtonPlaylist } from '@/modules/OrganizerButtonPlaylist'
import ConsoleCustom from "./modules/General/ConsoleCustom";
import ConsoleTesteur from "./modules/General/ConsoleTesteur";


type DataTransfer = {
    id: string
    dragstart: string
}


document.addEventListener("DOMContentLoaded", () => {
    if (OrganizerDragAndDropZone.valid()) {
        new DragAndDropEventManager().setupEvents();
        checkEmptyPlaylist()
        initOrderBadge()
        new SectionAdder().addEvent();
        new ScrollManager().addEvent();
    }
});

function initOrderBadge() {
    const cleanorder = new CleanOrderHandler()
    cleanorder.resetBadge()
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

class BadgeRenderer {
    public refreshSectionBadges(allSections: HTMLDivElement[]): void {
        for (const section of allSections) {
            if (section) {
                const listEl = section.getElementsByClassName('playlist-dragAndDrop') as HTMLCollectionOf<HTMLDivElement>;
                for (const element of listEl) {
                    if (element?.id) {
                        const buttonPlaylist = new OrganizerButtonPlaylist(element.id);
                        buttonPlaylist.removeBadge(false);
                        let order = 0;
                        if (element.dataset?.order) {
                            order = Number.parseInt(element.dataset.order);
                        }
                        buttonPlaylist.addBadge(order);
                    }
                }
            }
        }
    }

    public clearUnassociatedBadges(playlistNonAssociees: HTMLDivElement): void {
        if (playlistNonAssociees) {
            const listUnassociated = playlistNonAssociees.getElementsByClassName('playlist-dragAndDrop') as HTMLCollectionOf<HTMLDivElement>;
            for (const unassociated of listUnassociated) {
                if (unassociated?.id) {
                    const buttonPlaylist = new OrganizerButtonPlaylist(unassociated.id);
                    buttonPlaylist.removeBadge(true);
                }
            }
        }
    }
}

class CleanOrderHandler {
    allSections: HTMLDivElement[];
    playlistNonAssociees: HTMLDivElement;
    private readonly badgeRenderer: BadgeRenderer;

    constructor() {
        this.allSections = OrganizerDragAndDropZone.getAllSections();
        this.playlistNonAssociees = OrganizerDragAndDropZone.unassociatedPlaylists();
        this.badgeRenderer = new BadgeRenderer();
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
        return this;
    }

    trueReorder() {
        const maxSections = SectionConfig.getMaxSections();
        for (let i = 1; i <= maxSections; i++) {
            this.trueReorderSection(i);
        }
        return this;
    }

    resetBadge() {
        this.badgeRenderer.refreshSectionBadges(this.allSections);
        this.cleanUnsassociatedBadge();
        return this;
    }

    cleanUnsassociatedBadge() {
        this.badgeRenderer.clearUnassociatedBadges(this.playlistNonAssociees);
        return this;
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
    private readonly apiClient: OrganizerApiClient;

    constructor() {
        this.apiClient = new OrganizerApiClient();
    }

    public addMusic(btnPlaylist: OrganizerButtonPlaylist, newOrder: number, section: number) {
        this.send('POST', {
            idPlaylist: btnPlaylist.playlist.id,
            newOrder: newOrder,
            section: section
        }, section)
    }

    public removeMusic(btnPlaylist: OrganizerButtonPlaylist, section: number) {
        this.send('DELETE', {
            idPlaylist: btnPlaylist.playlist.id,
            section: section
        })
    }

    public updateMusic(btnPlaylist: OrganizerButtonPlaylist, newOrder: number, section: number) {
        this.send('UPDATE', {
            idPlaylist: btnPlaylist.playlist.id,
            newOrder: newOrder,
            section: section
        }, section)
    }

    public async insertSection(insertSection: number): Promise<boolean> {
        try {
            return await this.apiClient.insertSection(insertSection);
        } catch (error) {
            ConsoleCustom.error(error);
            return false;
        }
    }

    private send(method: string, body: {}, section?: number) {
        ConsoleTesteur.info(`Fetch called with method: ${method}, body: ${JSON.stringify(body)}, section: ${section}`);
        this.apiClient.request(method, body)
            .then(() => {
                const cleanorder = new CleanOrderHandler()
                cleanorder.resetBadge()
            })
            .catch(error => ConsoleCustom.error(error));
    }

}

class OrganizerApiClient {
    public async insertSection(insertSection: number): Promise<boolean> {
        const response = await this.request('UPDATE', {
            insertSection: insertSection
        });
        return response.ok;
    }

    public async request(method: string, body: {}): Promise<Response> {
        const url = OrganizerDragAndDropZone.getUrlFromAnySection();
        return fetch(url, {
            method: method,
            headers: {
                'X-CSRFToken': Csrf.getToken()!,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(body)
        });
    }
}

class PlaylistDropHandler {
    public handleSectionDrop(elementDragged: DragEvent, sectionEl: HTMLDivElement, sectionNumber: number): void {
        ConsoleTesteur.log('drop event on associées');

        elementDragged.preventDefault();
        const EDT = EventDataTransfert.getClassFromEvent(elementDragged);
        if (EDT.DataTransfer == null) return;

        const playlist = document.getElementById(EDT.DataTransfer.id) as HTMLDivElement;
        if (!playlist) {
            ConsoleTesteur.error(`Playlist element not found with id: ${EDT.DataTransfer.id}`);
            return;
        }

        const listHtmlPlaylist = [...sectionEl.getElementsByClassName('playlist-dragAndDrop')] as HTMLElement[];
        const btnPlaylist = new OrganizerButtonPlaylist(EDT.DataTransfer.id);
        const sendbackend = new SendBackendAction();

        let orderNewElement: number;
        const isFromAssociatedSection = EDT.DataTransfer.dragstart.startsWith('playlistAssociees');
        const isSameSection = EDT.DataTransfer.dragstart === `playlistAssociees-${sectionNumber}`;

        if (isFromAssociatedSection && isSameSection) {
            orderNewElement = this.handleSameSectionDrop(elementDragged, playlist, listHtmlPlaylist, sectionEl);
            if (orderNewElement > 0) {
                sendbackend.updateMusic(btnPlaylist, orderNewElement, sectionNumber);
            }
        } else if (isFromAssociatedSection) {
            orderNewElement = this.handleDifferentSectionDrop(elementDragged, playlist, listHtmlPlaylist, sectionEl);
            sendbackend.updateMusic(btnPlaylist, orderNewElement, sectionNumber);
        } else {
            orderNewElement = this.handleUnassociatedToAssociatedDrop(elementDragged, playlist, listHtmlPlaylist, sectionEl);
            sendbackend.addMusic(btnPlaylist, orderNewElement, sectionNumber);
        }

        checkEmptyPlaylist();
        new CleanOrderHandler().trueReorder().resetBadge();
    }

    public handleUnassociatedDrop(e: DragEvent, playlistNonAssociees: HTMLDivElement): void {
        ConsoleTesteur.log('drop event on non associées');

        e.preventDefault();
        const EDT = EventDataTransfert.getClassFromEvent(e);
        if (EDT.DataTransfer == null) return;
        if (EDT.DataTransfer.dragstart == 'playlistNonAssociees') return;

        const btnPlaylist = new OrganizerButtonPlaylist(EDT.DataTransfer.id);
        const playlist = document.getElementById(EDT.DataTransfer.id) as HTMLElement;

        if (!playlist) {
            ConsoleTesteur.error(`Playlist element not found with id: ${EDT.DataTransfer.id}`);
            return;
        }

        if (playlistNonAssociees) {
            playlistNonAssociees.appendChild(playlist);
        }
        checkEmptyPlaylist();
        new SendBackendAction().removeMusic(btnPlaylist, Number.parseInt(playlist.dataset.section!));
        new CleanOrderHandler().trueReorder().resetBadge();
    }

    private handleSameSectionDrop(elementDragged: DragEvent, playlist: HTMLDivElement, listHtmlPlaylist: HTMLElement[], sectionEl: HTMLDivElement): number {
        ConsoleTesteur.group('Updating music in the same section', sectionEl);
        ConsoleTesteur.log('listHtmlPlaylist', listHtmlPlaylist);

        if (listHtmlPlaylist.length === 1 && listHtmlPlaylist[0].id === playlist.id) {
            ConsoleTesteur.log('Only one element in section, no need to update');
            ConsoleTesteur.groupEnd();
            return 0;
        }

        const handler = new DropPointHandler(playlist, listHtmlPlaylist);
        playlist.remove();
        handler.insertElement(elementDragged);
        const newOrder = handler.getNewOrder();
        ConsoleTesteur.groupEnd();
        return newOrder;
    }

    private handleDifferentSectionDrop(elementDragged: DragEvent, playlist: HTMLDivElement, listHtmlPlaylist: HTMLElement[], sectionEl: HTMLDivElement): number {
        ConsoleTesteur.group('Updating music in the different section', sectionEl);
        ConsoleTesteur.log('listHtmlPlaylist', listHtmlPlaylist);
        const newOrder = this.insertPlaylistInSection(elementDragged, playlist, listHtmlPlaylist, sectionEl);
        ConsoleTesteur.groupEnd();
        return newOrder;
    }

    private handleUnassociatedToAssociatedDrop(elementDragged: DragEvent, playlist: HTMLDivElement, listHtmlPlaylist: HTMLElement[], sectionEl: HTMLDivElement): number {
        ConsoleTesteur.group('Adding music from unassociated to associated');
        const newOrder = this.insertPlaylistInSection(elementDragged, playlist, listHtmlPlaylist, sectionEl);
        ConsoleTesteur.groupEnd();
        return newOrder;
    }

    private insertPlaylistInSection(elementDragged: DragEvent, playlist: HTMLDivElement, listHtmlPlaylist: HTMLElement[], sectionEl: HTMLDivElement): number {
        if (listHtmlPlaylist.length === 0) {
            ConsoleTesteur.log('Section is empty, appending playlist directly');
            if (sectionEl && playlist) {
                sectionEl.appendChild(playlist);
                return 1;
            }
            return 0;
        }

        ConsoleTesteur.log('Section is not empty, inserting playlist');
        const handler = new DropPointHandler(playlist, listHtmlPlaylist);
        playlist.remove();
        handler.insertElement(elementDragged);
        return handler.getNewOrder();
    }
}

class DragAndDropEventManager {
    private readonly playlistNonAssociees: HTMLDivElement;
    private readonly allSections: HTMLDivElement[];
    private readonly dropHandler: PlaylistDropHandler;
    private static readonly BOUND_ATTR = 'data-dnd-bound';

    constructor() {
        this.playlistNonAssociees = OrganizerDragAndDropZone.unassociatedPlaylists();
        this.allSections = OrganizerDragAndDropZone.getAllSections();
        this.dropHandler = new PlaylistDropHandler();
    }

    public setupEvents(): void {
        if (this.playlistNonAssociees == null || this.allSections.length === 0) return;

        this.setupSectionEvents();
        this.setupUnassociatedPlaylistEvents();
    }

    private setupSectionEvents(): void {
        for (const sectionEl of this.allSections) {
            if (sectionEl.getAttribute(DragAndDropEventManager.BOUND_ATTR) === 'true') {
                continue;
            }

            const sectionNumber = Number.parseInt(sectionEl.dataset.section || '0');
            if (sectionNumber <= 0) {
                continue;
            }

            sectionEl.addEventListener('dragstart', (e: DragEvent) => {
                const EDT = new EventDataTransfert(e);
                const target = e.target! as HTMLDivElement;
                EDT.build(target.id, `playlistAssociees-${sectionNumber}`);
            });

            sectionEl.addEventListener('dragover', (e) => {
                e.preventDefault();
            });

            sectionEl.addEventListener('drop', (elementDragged: DragEvent) => {
                this.dropHandler.handleSectionDrop(elementDragged, sectionEl, sectionNumber);
            });

            sectionEl.setAttribute(DragAndDropEventManager.BOUND_ATTR, 'true');
        }
    }

    private setupUnassociatedPlaylistEvents(): void {
        if (this.playlistNonAssociees.getAttribute(DragAndDropEventManager.BOUND_ATTR) === 'true') {
            return;
        }

        this.playlistNonAssociees.addEventListener('dragstart', (e: DragEvent) => {
            const EDT = new EventDataTransfert(e);
            const target = e.target! as HTMLDivElement;
            EDT.build(target.id, 'playlistNonAssociees');
        });

        this.playlistNonAssociees.addEventListener('dragover', (e) => {
            e.preventDefault();
        });

        this.playlistNonAssociees.addEventListener('drop', (e: DragEvent) => {
            this.dropHandler.handleUnassociatedDrop(e, this.playlistNonAssociees);
        });

        this.playlistNonAssociees.setAttribute(DragAndDropEventManager.BOUND_ATTR, 'true');
    }
}




class SectionDomManager {
    public updateAccordionNode(accordionNode: HTMLElement, sectionNumber: number): void {
        const numSectionSpan = accordionNode.querySelector('.num-section') as HTMLSpanElement;
        if (numSectionSpan) {
            numSectionSpan.textContent = sectionNumber.toString();
        }

        const sectionContainer = accordionNode.querySelector('.section-container') as HTMLDivElement;
        if (sectionContainer) {
            sectionContainer.id = `associated-playlists-section-${sectionNumber}`;
            sectionContainer.dataset.section = sectionNumber.toString();

            const playlists = sectionContainer.getElementsByClassName('playlist-dragAndDrop') as HTMLCollectionOf<HTMLDivElement>;
            for (const playlist of playlists) {
                playlist.dataset.section = sectionNumber.toString();
            }
        }

        const sectionEmpty = accordionNode.querySelector('[class*="section-"][class*="-empty"]') as HTMLSpanElement;
        if (sectionEmpty) {
            sectionEmpty.className = sectionEmpty.className.replace(
                /section-\d+-empty/,
                `section-${sectionNumber}-empty`
            );
        }

        const accordionHeader = accordionNode.querySelector('.accordion-header') as HTMLHeadingElement;
        if (accordionHeader) {
            accordionHeader.id = `panelsSection-${sectionNumber}`;
        }

        const accordionButton = accordionNode.querySelector('.accordion-button') as HTMLButtonElement;
        if (accordionButton) {
            accordionButton.setAttribute('aria-controls', `panelsStayOpen-${sectionNumber}`);
            accordionButton.dataset.bsTarget = `#panelsStayOpen-${sectionNumber}`;
        }

        const accordionCollapse = accordionNode.querySelector('.accordion-collapse') as HTMLDivElement;
        if (accordionCollapse) {
            accordionCollapse.id = `panelsStayOpen-${sectionNumber}`;
            accordionCollapse.setAttribute('aria-labelledby', `panelsSection-${sectionNumber}`);
        }

        const insertButton = accordionNode.querySelector('.section-insert-before-button') as HTMLButtonElement;
        if (insertButton) {
            insertButton.dataset.insertBefore = sectionNumber.toString();
        }
    }

    public buildSectionNode(template: HTMLTemplateElement, sectionNumber: number): HTMLElement | null {
        const clone = template.content.cloneNode(true) as DocumentFragment;
        const accordionNode = clone.querySelector('.accordion') as HTMLElement;
        if (!accordionNode) {
            return null;
        }

        this.updateAccordionNode(accordionNode, sectionNumber);
        return accordionNode;
    }

    public shiftSectionsForInsertion(insertPosition: number): void {
        const maxSections = SectionConfig.getMaxSections();

        for (let currentSection = maxSections; currentSection >= insertPosition; currentSection--) {
            const sectionEl = OrganizerDragAndDropZone.associatedPlaylistsSection(currentSection);
            if (!sectionEl) {
                continue;
            }

            const accordionNode = sectionEl.closest('.accordion') as HTMLElement | null;
            if (!accordionNode) {
                continue;
            }

            const shiftedAccordionNode = accordionNode.cloneNode(true) as HTMLElement;
            this.updateAccordionNode(shiftedAccordionNode, currentSection + 1);
            accordionNode.replaceWith(shiftedAccordionNode);
        }
    }
}


class SectionAdder {

    private template: HTMLTemplateElement | null = null;
    private readonly sectionDomManager: SectionDomManager;

    constructor() {
        this.sectionDomManager = new SectionDomManager();
        this.setTemplate();
    }

    public addEvent() {
        const addSectionButton = document.getElementById('add-section-button');
        if (addSectionButton && this.template) {
            addSectionButton.addEventListener('click', () => {
                SectionConfig.refreshMaxSections();
                void this.addSectionAt(SectionConfig.getNextSectionNumber());
            });
        }

        const parentContainer = document.getElementById('associated-playlists-container');
        if (parentContainer && !parentContainer.dataset.insertSectionBound) {
            parentContainer.addEventListener('click', (event: Event) => {
                const target = event.target as HTMLElement;
                const insertButton = target.closest('.section-insert-before-button') as HTMLButtonElement | null;
                if (!insertButton?.dataset.insertBefore) {
                    return;
                }

                const insertPosition = Number.parseInt(insertButton.dataset.insertBefore);
                if (Number.isNaN(insertPosition) || insertPosition <= 0) {
                    return;
                }

                void this.addSectionAt(insertPosition);
            });

            parentContainer.dataset.insertSectionBound = 'true';
        }
    }

    private setTemplate(): boolean {
        this.template = document.getElementById('add-section-template') as HTMLTemplateElement;
        if (!this.template) {
            ConsoleTesteur.error('Template add-section-template not found');
            return false;
        }
        return true;
    }

    private async addSectionAt(insertPosition: number): Promise<void> {
        try {
            if (!this.template) {
                return;
            }

            SectionConfig.refreshMaxSections();
            const maxSectionsBeforeInsert = SectionConfig.getMaxSections();
            const nextSectionNumber = maxSectionsBeforeInsert + 1;
            const normalizedInsertPosition = Math.max(1, Math.min(insertPosition, nextSectionNumber));

            // Vérifier si on dépasse la limite
            if (nextSectionNumber > Number.parseInt(this.template.dataset.maxSection!)) {
                ConsoleTesteur.warn(`Maximum number of sections reached (${this.template.dataset.maxSection})`);
                return;
            }

            const shouldPersistShift = normalizedInsertPosition <= maxSectionsBeforeInsert;
            if (shouldPersistShift) {
                const sendbackend = new SendBackendAction();
                const persisted = await sendbackend.insertSection(normalizedInsertPosition);
                if (!persisted) {
                    ConsoleCustom.warn(`Failed to persist section insertion at ${normalizedInsertPosition}`);
                    return;
                }
            }

            const parentContainer = document.getElementById('associated-playlists-container');
            if (!parentContainer) {
                return;
            }

            if (shouldPersistShift) {
                this.sectionDomManager.shiftSectionsForInsertion(normalizedInsertPosition);
            }

            const newSectionNode = this.sectionDomManager.buildSectionNode(this.template, normalizedInsertPosition);
            if (!newSectionNode) {
                return;
            }

            // L'ancienne ancre peut être remplacée pendant le décalage; on la recalcul après shift.
            let insertAnchor: HTMLElement | null = null;
            if (shouldPersistShift) {
                const shiftedTargetSection = OrganizerDragAndDropZone.associatedPlaylistsSection(normalizedInsertPosition + 1);
                insertAnchor = shiftedTargetSection?.closest('.accordion') as HTMLElement | null;
            }

            if (insertAnchor?.parentElement === parentContainer) {
                insertAnchor.before(newSectionNode);
            } else {
                parentContainer.appendChild(newSectionNode);
            }

            SectionConfig.refreshMaxSections();
            ConsoleTesteur.info(`Section ${normalizedInsertPosition} inserted successfully`);
            new DragAndDropEventManager().setupEvents();
            checkEmptyPlaylist();
            new CleanOrderHandler().resetBadge();
        } catch (error) {
            ConsoleCustom.error('Failed to insert section', error);
        }
    }
}



class ScrollManager {
    private scrollInterval: ReturnType<typeof setInterval> | null = null;
    private readonly scrollSpeed: number; // pixels per interval
    private readonly scrollZone: number; // pixels from edge to trigger scroll

    constructor() {
        this.scrollZone = window.innerHeight * 0.15;
        this.scrollSpeed = window.innerHeight * 0.3;
    }

    public addEvent() {
        // Add dragover event to document to handle auto-scroll
        document.addEventListener('dragover', (e) => {
            e.preventDefault();

            const mouseY = e.clientY;
            const windowHeight = window.innerHeight;

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

        document.addEventListener('drop', (_) => {
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




