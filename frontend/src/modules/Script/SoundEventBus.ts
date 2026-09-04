export type SoundEventName = 'music:ended' | 'music:stopped';

export interface SoundEventPayload {
    playlistId: string;
    token: string | null;
}

type SoundEventListener = (payload: SoundEventPayload) => void;

/**
 * Bus d'évènements audio permettant au moteur de script de réagir à la fin
 * ou à l'arrêt d'une lecture sans coupler MusicElement au moteur.
 */
class SoundEventBus {
    private static readonly listeners = new Map<SoundEventName, Set<SoundEventListener>>();

    /**
     * Abonne un écouteur à un évènement audio.
     * @returns Fonction de désabonnement
     */
    static on(eventName: SoundEventName, listener: SoundEventListener): () => void {
        let listeners = SoundEventBus.listeners.get(eventName);
        if (!listeners) {
            listeners = new Set<SoundEventListener>();
            SoundEventBus.listeners.set(eventName, listeners);
        }
        listeners.add(listener);
        return () => {
            listeners!.delete(listener);
        };
    }

    static emit(eventName: SoundEventName, payload: SoundEventPayload): void {
        const listeners = SoundEventBus.listeners.get(eventName);
        if (!listeners) return;
        for (const listener of Array.from(listeners)) {
            listener(payload);
        }
    }

    static reset(): void {
        SoundEventBus.listeners.clear();
    }
}

export default SoundEventBus;
