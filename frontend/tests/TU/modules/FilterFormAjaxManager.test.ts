import { describe, expect, it, vi } from 'vitest';
import FilterFormAjaxManager from '@/modules/Filter/FilterFormAjaxManager';

describe('FilterFormAjaxManager', () => {
    it('collects trimmed non-empty filters and reports changes', () => {
        document.body.innerHTML = `
            <div id="filters">
                <select name="genre" data-edit-mode-filter="true"><option value=" jazz " selected>Jazz</option></select>
                <select name="mood" data-edit-mode-filter="true"><option value="  " selected>Any</option></select>
            </div>
        `;
        const container = document.getElementById('filters')!;
        const onFiltersChange = vi.fn();
        const manager = new FilterFormAjaxManager(container, onFiltersChange);

        expect(manager.collectFilters()).toEqual({ genre: 'jazz' });
        manager.bind();
        container.querySelector('select')!.dispatchEvent(new Event('change'));

        expect(onFiltersChange).toHaveBeenCalledWith({ genre: 'jazz' });
    });
});