import { IAudioAdapter } from '@/modules/Audio/IAudioAdapter';
import AudioContextManager from '@/modules/Audio/AudioContextManager';

class WebAudioAdapter implements IAudioAdapter {
    private readonly audioElement: HTMLAudioElement;
    private readonly gainNode: GainNode | null;

    constructor(audioElement: HTMLAudioElement) {
        this.audioElement = audioElement;
        this.gainNode = AudioContextManager.getOrCreateGainNode(audioElement);
    }

    static isSupported(): boolean {
        return AudioContextManager.isSupported();
    }

    getSource(): string {
        return this.audioElement.src;
    }

    setSource(source: string): void {
        this.audioElement.src = source;
    }

    setDatasetValue(key: string, value: string): void {
        this.audioElement.dataset[key] = value;
    }

    getDatasetValue(key: string): string | undefined {
        return this.audioElement.dataset[key];
    }

    setPreload(preload: HTMLMediaElement['preload']): void {
        this.audioElement.preload = preload;
    }

    setControls(controls: boolean): void {
        this.audioElement.controls = controls;
    }

    setClassName(className: string): void {
        this.audioElement.className = className;
    }

    addClass(className: string): void {
        this.audioElement.classList.add(className);
    }

    getCurrentTime(): number {
        return this.audioElement.currentTime;
    }

    setCurrentTime(value: number): void {
        this.audioElement.currentTime = value;
    }

    getDuration(): number {
        return this.audioElement.duration;
    }

    getReadyState(): number {
        return this.audioElement.readyState;
    }

    setVolume(value: number): void {
        const clamped = Math.min(1, Math.max(0, value));
        if (this.gainNode) {
            this.gainNode.gain.value = clamped;
            return;
        }

        this.audioElement.volume = clamped;
    }

    addEventListener(type: string, listener: EventListenerOrEventListenerObject, options?: boolean | AddEventListenerOptions): void {
        this.audioElement.addEventListener(type, listener, options);
    }

    removeEventListener(type: string, listener: EventListenerOrEventListenerObject, options?: boolean | EventListenerOptions): void {
        this.audioElement.removeEventListener(type, listener, options);
    }

    appendTo(parent: HTMLElement): void {
        parent.appendChild(this.audioElement);
    }

    remove(): void {
        this.audioElement.remove();
    }

    async play(): Promise<void> {
        await AudioContextManager.resumeContext();
        await this.audioElement.play();
    }

    getError(): MediaError | null {
        return this.audioElement.error;
    }
}

export default WebAudioAdapter;
