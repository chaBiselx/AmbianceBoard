const sliderSelector = '.horizontal-slider-input';
let listenersInitialized = false;

export function updateHorizontalSliderOutput(input: HTMLInputElement): void {
    const output = input.parentElement?.querySelector<HTMLOutputElement>('.horizontal-slider-output');
    if (!output) return;

    const min = Number(input.min || 0);
    const max = Number(input.max || 100);
    const range = max - min;
    const progress = range > 0 ? Math.min(1, Math.max(0, (input.valueAsNumber - min) / range)) : 0;

    output.textContent = input.value;
    output.style.setProperty('--slider-progress', `${progress * 100}%`);
}

export function refreshHorizontalSliderOutputs(root: ParentNode = document): void {
    root.querySelectorAll<HTMLInputElement>(sliderSelector).forEach(updateHorizontalSliderOutput);
}

export function initializeHorizontalSliderOutputs(root: ParentNode = document): void {
    refreshHorizontalSliderOutputs(root);
    if (listenersInitialized) return;

    document.addEventListener('input', (event: Event) => {
        const input = event.target;
        if (input instanceof HTMLInputElement && input.matches(sliderSelector)) {
            updateHorizontalSliderOutput(input);
        }
    });

    listenersInitialized = true;
}
