class MixerElement {
    private readonly mixerElement: HTMLInputElement | null;

    constructor(typeMixer: string) {
        this.mixerElement = Array.from(document.querySelectorAll('.mixer-playlist'))
            .find((element): element is HTMLInputElement =>
                element instanceof HTMLInputElement && element.dataset.type === typeMixer,
            ) ?? null;
    }

    update(value: number): void {
        if (!this.mixerElement) return;
        this.mixerElement.value = value.toString();
        this.mixerElement.dispatchEvent(new Event('input'));
    }
}

export { MixerElement };
