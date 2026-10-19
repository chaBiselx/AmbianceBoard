import { beforeEach, describe, expect, it } from 'vitest';
import { initializeHorizontalSliderOutputs } from '@/modules/HorizontalSliderOutput';

describe('HorizontalSliderOutput', () => {
    beforeEach(() => {
        document.body.innerHTML = `
            <form class="mixer-playlist-update-container">
                <input class="horizontal-slider-input" type="range" min="10" max="100" value="55">
                <output class="horizontal-slider-output"></output>
            </form>
        `;
    });

    it('updates the displayed value and progress color without measuring slider geometry', () => {
        const input = document.querySelector<HTMLInputElement>('.horizontal-slider-input')!;
        initializeHorizontalSliderOutputs();

        const output = document.querySelector<HTMLOutputElement>('.horizontal-slider-output')!;
        expect(output.textContent).toBe('55');
        expect(output.style.getPropertyValue('--slider-progress')).toBe('50%');

        input.value = '100';
        input.dispatchEvent(new Event('input', { bubbles: true }));

        expect(output.textContent).toBe('100');
        expect(output.style.getPropertyValue('--slider-progress')).toBe('100%');
        expect(output.style.left).toBe('');
    });
});
