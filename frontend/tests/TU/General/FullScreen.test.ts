import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import FullScreen from '../../../src/modules/General/FullScreen';
import BootstrapComponentInitializer from '../../../src/modules/General/BootstrapComponentInitializer';

describe('FullScreen', () => {
    beforeEach(() => {
        document.body.innerHTML = `
            <button id="hideAll"></button>
            <button id="showBaseLayoutButton"></button>
            <div class="fullScreen-element"></div>
            <span class="fullScreen-element-inline"></span>
            <main id="mainBody"></main>
            <section id="main-content"></section>
        `;
    });

    afterEach(() => {
        vi.useRealTimers();
        vi.restoreAllMocks();
    });

    it('toggles fullscreen classes and hides tooltips after each click', () => {
        vi.useFakeTimers();
        const hideTooltips = vi.spyOn(BootstrapComponentInitializer, 'hideAllTooltips').mockImplementation(() => {});

        new FullScreen().addEvent();
        document.getElementById('hideAll')!.click();

        expect(document.querySelector('.fullScreen-element')!.classList.contains('d-none')).toBe(true);
        expect(document.querySelector('.fullScreen-element-inline')!.classList.contains('d-inline')).toBe(true);
        expect(document.getElementById('mainBody')!.classList.contains('p-0')).toBe(true);
        expect(document.getElementById('main-content')!.classList.contains('py-lg-5')).toBe(true);
        vi.runAllTimers();
        expect(hideTooltips).toHaveBeenCalledTimes(2);
    });
});
