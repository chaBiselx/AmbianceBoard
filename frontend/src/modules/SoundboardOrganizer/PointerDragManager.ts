import { PlaylistDropHandler } from './PlaylistDropHandler';

class PointerDragState {
    private static _pointerId: number | null = null;
    private static _element: HTMLElement | null = null;
    private static _ghost: HTMLElement | null = null;
    private static _sourceZone = '';
    private static _startX = 0;
    private static _startY = 0;
    private static _offsetX = 0;
    private static _offsetY = 0;
    private static _dragging = false;

    public static get pointerId(): number | null { return this._pointerId; }
    public static set pointerId(value: number | null) { this._pointerId = value; }

    public static get element(): HTMLElement | null { return this._element; }
    public static set element(value: HTMLElement | null) { this._element = value; }

    public static get ghost(): HTMLElement | null { return this._ghost; }
    public static set ghost(value: HTMLElement | null) { this._ghost = value; }

    public static get sourceZone(): string { return this._sourceZone; }
    public static set sourceZone(value: string) { this._sourceZone = value; }

    public static get startX(): number { return this._startX; }
    public static set startX(value: number) { this._startX = value; }

    public static get startY(): number { return this._startY; }
    public static set startY(value: number) { this._startY = value; }

    public static get offsetX(): number { return this._offsetX; }
    public static set offsetX(value: number) { this._offsetX = value; }

    public static get offsetY(): number { return this._offsetY; }
    public static set offsetY(value: number) { this._offsetY = value; }

    public static get dragging(): boolean { return this._dragging; }
    public static set dragging(value: boolean) { this._dragging = value; }

    public static reset(): void {
        this._pointerId = null;
        this._element = null;
        this._ghost = null;
        this._sourceZone = '';
        this._startX = 0;
        this._startY = 0;
        this._offsetX = 0;
        this._offsetY = 0;
        this._dragging = false;
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