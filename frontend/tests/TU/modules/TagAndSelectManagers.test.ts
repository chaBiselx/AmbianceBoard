import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { TagManager } from '@/modules/TagManager';
import { SelectManager } from '@/modules/SelectManager';

describe('TagManager and SelectManager', () => {
    beforeEach(() => {
        const url = new URL('http://localhost:3000/?existing=ok&page=4');
        // @ts-ignore
        delete globalThis.location;
        globalThis.location = { ...globalThis.location, href: url.href, replace: vi.fn() };
    });

    afterEach(() => {
        vi.restoreAllMocks();
        document.body.innerHTML = '';
    });

    it('sets the selected tag and resets pagination', () => {
        document.body.innerHTML = `
            <form class="dynamic-filter-search">
                <a class="tag-element-redirect" data-tag="ambient">Ambient</a>
            </form>
        `;

        new TagManager().addEventListeners();
        document.querySelector<HTMLElement>('.tag-element-redirect')!.click();

        expect(globalThis.location.replace).toHaveBeenCalledWith(
            'http://localhost:3000/?existing=ok&tag=ambient'
        );
    });

    it('does not navigate when the clicked tag has no value', () => {
        document.body.innerHTML = `
            <form class="dynamic-filter-search">
                <a class="tag-element-redirect">Unfiltered</a>
            </form>
        `;

        new TagManager().addEventListeners();
        document.querySelector<HTMLElement>('.tag-element-redirect')!.click();

        expect(globalThis.location.replace).not.toHaveBeenCalled();
    });

    it('sets the selected filter and resets pagination', () => {
        document.body.innerHTML = `
            <form class="dynamic-filter-search">
                <select class="select-element-redirect" name="genre">
                    <option value="jazz" selected>Jazz</option>
                </select>
            </form>
        `;

        new SelectManager().addEventListeners();
        document.querySelector<HTMLSelectElement>('.select-element-redirect')!
            .dispatchEvent(new Event('change'));

        expect(globalThis.location.replace).toHaveBeenCalledWith(
            'http://localhost:3000/?existing=ok&genre=jazz'
        );
    });
});