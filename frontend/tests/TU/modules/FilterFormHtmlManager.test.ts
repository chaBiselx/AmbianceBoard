import { beforeEach, describe, expect, it, vi } from 'vitest';
import FilterFormHtmlManager from '@/modules/Filter/FilterFormHtmlManager';

describe('FilterFormHtmlManager', () => {
    beforeEach(() => {
        document.body.innerHTML = `
            <form data-filter-form>
                <select data-filter-select><option value="all">All</option></select>
                <input type="text">
                <input type="search">
            </form>
            <form><input type="text"></form>
        `;
    });

    it('submits a filter form when a select changes', () => {
        const form = document.querySelector<HTMLFormElement>('[data-filter-form]')!;
        const submit = vi.spyOn(form, 'submit').mockImplementation(() => {});
        new FilterFormHtmlManager().init();

        form.querySelector('select')!.dispatchEvent(new Event('change'));

        expect(submit).toHaveBeenCalledOnce();
    });

    it.each(['text', 'search'])('submits on Enter in a %s input only', (type) => {
        const form = document.querySelector<HTMLFormElement>('[data-filter-form]')!;
        const submit = vi.spyOn(form, 'submit').mockImplementation(() => {});
        const input = form.querySelector<HTMLInputElement>(`input[type="${type}"]`)!;
        new FilterFormHtmlManager().init();

        input.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape', bubbles: true }));
        expect(submit).not.toHaveBeenCalled();

        const enter = new KeyboardEvent('keydown', { key: 'Enter', bubbles: true, cancelable: true });
        input.dispatchEvent(enter);

        expect(enter.defaultPrevented).toBe(true);
        expect(submit).toHaveBeenCalledOnce();
    });
});