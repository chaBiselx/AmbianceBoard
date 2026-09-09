export interface IAudioAdapter {
    getSource(): string;
    setSource(source: string): void;

    setDatasetValue(key: string, value: string): void;
    getDatasetValue(key: string): string | undefined;

    setPreload(preload: HTMLMediaElement['preload']): void;
    setControls(controls: boolean): void;

    setClassName(className: string): void;
    addClass(className: string): void;

    getCurrentTime(): number;
    setCurrentTime(value: number): void;
    getDuration(): number;
    getReadyState(): number;

    setVolume(value: number): void;

    addEventListener(type: string, listener: EventListenerOrEventListenerObject, options?: boolean | AddEventListenerOptions): void;
    removeEventListener(type: string, listener: EventListenerOrEventListenerObject, options?: boolean | EventListenerOptions): void;

    appendTo(parent: HTMLElement): void;
    remove(): void;

    play(): Promise<void>;

    getError(): MediaError | null;
}
