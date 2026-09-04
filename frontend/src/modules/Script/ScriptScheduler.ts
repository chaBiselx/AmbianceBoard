/**
 * Ordonnanceur des étapes d'un script : centralise les timers et les
 * désabonnements afin qu'un arrêt du script annule tout d'un coup.
 */
class ScriptScheduler {
    private readonly timeouts = new Set<ReturnType<typeof setTimeout>>();
    private readonly disposers: Array<() => void> = [];
    private disposed = false;

    scheduleAfter(delayMs: number, callback: () => void): void {
        if (this.disposed) return;
        const timeoutId = setTimeout(() => {
            this.timeouts.delete(timeoutId);
            if (this.disposed) return;
            callback();
        }, Math.max(0, delayMs));
        this.timeouts.add(timeoutId);
    }

    addDisposer(disposer: () => void): void {
        if (this.disposed) {
            disposer();
            return;
        }
        this.disposers.push(disposer);
    }

    isDisposed(): boolean {
        return this.disposed;
    }

    dispose(): void {
        if (this.disposed) return;
        this.disposed = true;
        for (const timeoutId of this.timeouts) {
            clearTimeout(timeoutId);
        }
        this.timeouts.clear();
        for (const disposer of this.disposers.splice(0, this.disposers.length)) {
            disposer();
        }
    }
}

export default ScriptScheduler;
