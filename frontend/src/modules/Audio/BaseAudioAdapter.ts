import { IAudioAdapter } from '@/modules/Audio/IAudioAdapter';

abstract class BaseAudioAdapter implements IAudioAdapter {
    protected readonly audioElement: HTMLAudioElement;

    constructor(audioElement: HTMLAudioElement) {
        this.audioElement = audioElement;
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
        this.audioElement.volume = Math.min(1, Math.max(0, value));
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

    abstract play(): Promise<void>;

    getError(): MediaError | null {
        return this.audioElement.error;
    }
}

export default BaseAudioAdapter;
