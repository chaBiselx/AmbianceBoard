import { ButtonPlaylistFinder } from '@/modules/ButtonPlaylist';
import { SoundBoardManager } from '@/modules/SoundBoardManager';
import { ScriptStepHandle } from '@/modules/Script/IScriptAction';
import SoundEventBus from '@/modules/Script/SoundEventBus';

/**
 * Poignée d'une action instantanée : sa fin est immédiate, ce qui permet de
 * chaîner une étape ON_STEP_END dessus.
 */
export class InstantStepHandle implements ScriptStepHandle {
    onEnd(callback: () => void): void {
        callback();
    }

    release(): void {
        // Aucun abonnement à libérer.
    }

    stop(): void {
        // Aucun effet à annuler.
    }
}

/**
 * Poignée d'une lecture de playlist : sa fin correspond à la fin naturelle du
 * son joué pour cette playlist.
 */
export class PlaylistStepHandle implements ScriptStepHandle {
    private readonly callbacks: Array<() => void> = [];
    private ended = false;
    private unsubscribe: (() => void) | null;

    constructor(private readonly playlistId: string) {
        this.unsubscribe = SoundEventBus.on('music:ended', (payload) => {
            if (payload.playlistId !== this.playlistId) return;
            this.markEnded();
        });
    }

    onEnd(callback: () => void): void {
        if (this.ended) {
            callback();
            return;
        }
        this.callbacks.push(callback);
    }

    release(): void {
        this.unsubscribe?.();
        this.unsubscribe = null;
        this.callbacks.length = 0;
    }

    stop(): void {
        const alreadyEnded = this.ended;
        this.release();
        if (alreadyEnded) return;
        const buttonPlaylist = ButtonPlaylistFinder.search(this.playlistId);
        if (buttonPlaylist?.isActive()) {
            buttonPlaylist.disactive();
            SoundBoardManager.removePlaylist(buttonPlaylist);
        }
    }

    private markEnded(): void {
        if (this.ended) return;
        this.ended = true;
        this.unsubscribe?.();
        this.unsubscribe = null;
        const callbacks = this.callbacks.splice(0, this.callbacks.length);
        for (const callback of callbacks) {
            callback();
        }
    }
}
