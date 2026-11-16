import { beforeEach, describe, expect, it, vi } from 'vitest';
import FilterFormDate from '@/modules/Filter/FilterFormDate';

describe('FilterFormDate', () => {
    beforeEach(() => {
        document.body.innerHTML = `
            <form data-filter-form>
                <input type="date" name="date_from" data-filter-date-range>
                <input type="date" name="date_to" data-filter-date-range>
            </form>
            <form><input type="date" data-filter-date-range></form>
        `;
    });

    it('submits the filter form when either date range input changes', () => {
        const form = document.querySelector<HTMLFormElement>('[data-filter-form]')!;
        const submit = vi.spyOn(form, 'submit').mockImplementation(() => {});
        new FilterFormDate().init();

        for (const input of form.querySelectorAll<HTMLInputElement>('[data-filter-date-range]')) {
            input.dispatchEvent(new Event('change'));
        }

        expect(submit).toHaveBeenCalledTimes(2);
    });

    it('does not bind date inputs outside filter forms', () => {
        const form = document.querySelectorAll<HTMLFormElement>('form')[1];
        const submit = vi.spyOn(form, 'submit').mockImplementation(() => {});
        new FilterFormDate().init();

        form.querySelector('input')!.dispatchEvent(new Event('change'));

        expect(submit).not.toHaveBeenCalled();
    });
});
