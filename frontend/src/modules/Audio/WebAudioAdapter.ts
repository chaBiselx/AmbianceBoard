import BaseAudioAdapter from '@/modules/Audio/BaseAudioAdapter';
import AudioContextManager from '@/modules/Audio/AudioContextManager';

class WebAudioAdapter extends BaseAudioAdapter {
    private readonly gainNode: GainNode | null;

    constructor(audioElement: HTMLAudioElement) {
        super(audioElement);
        this.gainNode = AudioContextManager.getOrCreateGainNode(audioElement);
    }

    static isSupported(): boolean {
        return AudioContextManager.isSupported();
    }

    override setVolume(value: number): void {
        const clamped = Math.min(1, Math.max(0, value));
        if (this.gainNode) {
            this.gainNode.gain.value = clamped;
            return;
        }

        super.setVolume(clamped);
    }

    async play(): Promise<void> {
        await AudioContextManager.resumeContext();
        await this.audioElement.play();
    }
}

export default WebAudioAdapter;
