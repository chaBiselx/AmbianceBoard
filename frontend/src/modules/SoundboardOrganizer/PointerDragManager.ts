import { PlaylistDropHandler } from './PlaylistDropHandler';

class PointerDragState {
    public static pointerId: number | null = null;
    public static element: HTMLElement | null = null;
    public static ghost: HTMLElement | null = null;
    public static sourceZone = '';
    public static startX = 0;
    public static startY = 0;
    public static offsetX = 0;
    public static offsetY = 0;
    public static dragging = false;

    public static reset(): void {
        this.pointerId = null;
        this.element = null;
        this.ghost = null;
        this.sourceZone = '';
        this.startX = 0;
        this.startY = 0;
        this.offsetX = 0;
        this.offsetY = 0;
        this.dragging = false;
    }
}

export class PointerDragManager {
    private static readonly dragThreshold = 8;
    private static bound = false;
    private readonly dropHandler = new PlaylistDropHandler();

    public setupEvents(): void {
        if (PointerDragManager.bound) return;

        document.addEventListener('dragstart', this.preventNativeDrag, { capture: true });
        document.addEventListener('dragover', this.allowNativeDrop, { capture: true });
        document.addEventListener('drop', this.preventNativeDrop, { capture: true });
        document.querySelectorAll<HTMLElement>('.playlist-dragAndDrop').forEach(element => {
            element.draggable = false;
            element.style.touchAction = 'none';
        });
        document.addEventListener('pointerdown', this.onPointerDown.bind(this), { passive: false });
        window.addEventListener('pointermove', this.onPointerMove.bind(this), { passive: false });
        window.addEventListener('pointerup', this.onPointerUp.bind(this), { passive: false });
        window.addEventListener('pointercancel', this.onPointerCancel.bind(this), { passive: false });
        document.addEventListener('lostpointercapture', this.onPointerCancel.bind(this), { passive: false });
        PointerDragManager.bound = true;
    }

    private preventNativeDrag(event: DragEvent): void {
        if ((event.target as HTMLElement | null)?.closest('.playlist-dragAndDrop')) {
            event.preventDefault();
            event.stopPropagation();
        }
    }

    private allowNativeDrop(event: DragEvent): void {
        if ((event.target as HTMLElement | null)?.closest('.zone-dragAndDrop')) event.preventDefault();
    }

    private preventNativeDrop(event: DragEvent): void {
        if ((event.target as HTMLElement | null)?.closest('.zone-dragAndDrop, .playlist-dragAndDrop')) {
            event.preventDefault();
            event.stopPropagation();
        }
    }

    private onPointerDown(event: PointerEvent): void {
        if ((event.pointerType === 'mouse' && event.button !== 0) || PointerDragState.dragging) return;
        const element = (event.target as HTMLElement | null)?.closest<HTMLElement>('.playlist-dragAndDrop');
        if (!element) return;

        event.preventDefault();
        PointerDragState.pointerId = event.pointerId;
        PointerDragState.element = element;
        PointerDragState.startX = event.clientX;
        PointerDragState.startY = event.clientY;
        PointerDragState.sourceZone = this.resolveSourceZone(element);
        document.body.classList.add('dragging-active');
        try {
            element.setPointerCapture(event.pointerId);
        } catch {}
    }

    private onPointerMove(event: PointerEvent): void {
        if (PointerDragState.pointerId !== event.pointerId || !PointerDragState.element) return;
        if (!PointerDragState.dragging) {
            if (Math.hypot(event.clientX - PointerDragState.startX, event.clientY - PointerDragState.startY) < PointerDragManager.dragThreshold) return;
            this.startDrag(event);
        }
        event.preventDefault();
        this.moveGhost(event);
        this.updateHoverTarget(event);
    }

    private onPointerUp(event: PointerEvent): void {
        if (PointerDragState.pointerId !== event.pointerId) return;
        try {
            const element = PointerDragState.element;
            const zone = PointerDragState.dragging ? this.zoneAtPoint(event.clientX, event.clientY) : null;
            if (!element || !zone) return;
            const dragInfo = { id: element.id, dragstart: PointerDragState.sourceZone };
            if (zone.id === 'unassociated-playlists') this.dropHandler.handleUnassociatedDrop(event, zone as HTMLDivElement, dragInfo);
            else if (zone.dataset.section) this.dropHandler.handleSectionDrop(event, zone as HTMLDivElement, Number.parseInt(zone.dataset.section), dragInfo);
        } finally {
            this.cleanup();
        }
    }

    private onPointerCancel(event: PointerEvent): void {
        if (PointerDragState.pointerId === null || event.pointerId === PointerDragState.pointerId) this.cleanup();
    }

    private startDrag(event: PointerEvent): void {
        const element = PointerDragState.element!;
        const rect = element.getBoundingClientRect();
        PointerDragState.offsetX = event.clientX - rect.left;
        PointerDragState.offsetY = event.clientY - rect.top;
        PointerDragState.dragging = true;
        const ghost = element.cloneNode(true) as HTMLElement;
        ghost.removeAttribute('id');
        ghost.className = 'drag-ghost';
        Object.assign(ghost.style, { position: 'fixed', left: '0px', top: '0px', margin: '0', width: `${rect.width}px`, pointerEvents: 'none' });
        document.body.appendChild(ghost);
        PointerDragState.ghost = ghost;
        element.classList.add('dragging-source');
        this.moveGhost(event);
    }

    private moveGhost(event: PointerEvent): void {
        PointerDragState.ghost?.style.setProperty('transform', `translate(${event.clientX - PointerDragState.offsetX}px, ${event.clientY - PointerDragState.offsetY}px)`);
    }

    private updateHoverTarget(event: PointerEvent): void {
        document.querySelectorAll('.zone-dragAndDrop.drag-over').forEach(element => element.classList.remove('drag-over'));
        this.zoneAtPoint(event.clientX, event.clientY)?.classList.add('drag-over');
    }

    private zoneAtPoint(x: number, y: number): HTMLElement | null {
        const ghost = PointerDragState.ghost;
        if (ghost) ghost.style.display = 'none';
        const zone = (document.elementFromPoint(x, y) as HTMLElement | null)?.closest<HTMLElement>('.zone-dragAndDrop') || null;
        if (ghost) ghost.style.display = '';
        return zone;
    }

    private resolveSourceZone(element: HTMLElement): string {
        const section = element.closest<HTMLElement>('.section-container');
        return section?.dataset.section ? `playlistAssociees-${section.dataset.section}` : 'playlistNonAssociees';
    }

    private cleanup(): void {
        PointerDragState.element?.classList.remove('dragging-source');
        PointerDragState.ghost?.remove();
        document.querySelectorAll('.dragging-source, .zone-dragAndDrop.drag-over').forEach(element => element.classList.remove('dragging-source', 'drag-over'));
        document.body.classList.remove('dragging-active');
        PointerDragState.reset();
    }
}

export function isPointerDragging(): boolean {
    return PointerDragState.dragging;
}