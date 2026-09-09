import { isPointerDragging } from './PointerDragManager';

export class ScrollManager {
    private scrollInterval: ReturnType<typeof setInterval> | null = null;
    private readonly scrollZone = window.innerHeight * 0.15;
    private readonly scrollSpeed = window.innerHeight * 0.3;

    public addEvent(): void {
        document.addEventListener('pointermove', event => {
            if (!isPointerDragging()) return;
            if (event.clientY < this.scrollZone) this.startAutoScroll('up');
            else if (event.clientY > window.innerHeight - this.scrollZone) this.startAutoScroll('down');
            else this.stopAutoScroll();
        });
        document.addEventListener('pointerup', () => this.stopAutoScroll());
        document.addEventListener('pointercancel', () => this.stopAutoScroll());
    }

    private startAutoScroll(direction: 'up' | 'down'): void {
        if (this.scrollInterval) return;
        this.scrollInterval = setInterval(() => {
            window.scrollBy(0, direction === 'up' ? -this.scrollSpeed : this.scrollSpeed);
            if (window.scrollY === 0 || window.innerHeight + window.scrollY >= document.body.offsetHeight) this.stopAutoScroll();
        }, 16);
    }

    private stopAutoScroll(): void {
        if (!this.scrollInterval) return;
        clearInterval(this.scrollInterval);
        this.scrollInterval = null;
    }
}