class AudioContextManager {
    private static context: AudioContext | null = null;
    private static readonly sourceNodes = new WeakMap<HTMLMediaElement, MediaElementAudioSourceNode>();
    private static readonly gainNodes = new WeakMap<HTMLMediaElement, GainNode>();
    private static unlockRegistered = false;

    static isSupported(): boolean {
        return typeof window !== 'undefined' && (window.AudioContext !== undefined ||  (window as any).webkitAudioContext !== undefined);
    }

    static getContext(): AudioContext | null {
        if (!this.isSupported()) {
            return null;
        }

        if (!this.context) {
            const AudioContextConstructor = window.AudioContext || (window as any).webkitAudioContext;
            this.context = new AudioContextConstructor();
            this.registerUnlockHandlers();
        }

        return this.context;
    }

    static async resumeContext(): Promise<void> {
        const context = this.getContext();
        if (!context) {
            return;
        }

        if (context.state === 'suspended') {
            try {
                await context.resume();
            } catch {
                // Ignore resume errors here: play() will still surface if user gesture is missing.
            }
        }
    }

    static getOrCreateGainNode(audioElement: HTMLAudioElement): GainNode | null {
        const context = this.getContext();
        if (!context) {
            return null;
        }

        let gainNode = this.gainNodes.get(audioElement);
        if (gainNode) {
            return gainNode;
        }

        let sourceNode = this.sourceNodes.get(audioElement);
        if (!sourceNode) {
            sourceNode = context.createMediaElementSource(audioElement);
            this.sourceNodes.set(audioElement, sourceNode);
        }

        gainNode = context.createGain();
        sourceNode.connect(gainNode);
        gainNode.connect(context.destination);
        this.gainNodes.set(audioElement, gainNode);

        return gainNode;
    }

    private static registerUnlockHandlers(): void {
        if (this.unlockRegistered || typeof document === 'undefined') {
            return;
        }

        this.unlockRegistered = true;

        const unlock = () => {
            this.resumeContext();
        };

        document.addEventListener('touchstart', unlock, { passive: true });
        document.addEventListener('touchend', unlock, { passive: true });
        document.addEventListener('click', unlock, { passive: true });
    }
}

export default AudioContextManager;
