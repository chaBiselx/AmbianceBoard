type FiltersRecord = Record<string, string>;
type OnFiltersChange = (filters: FiltersRecord) => void;

/**
 * Gère les filtres AJAX dans un conteneur dynamique (modal, panel).
 * Cible les <select data-edit-mode-filter="true"> et appelle le callback
 * à chaque changement avec l'ensemble des valeurs courantes.
 */
class FilterFormAjaxManager {
    private readonly container: HTMLElement;
    private readonly onFiltersChange: OnFiltersChange;

    constructor(container: HTMLElement, onFiltersChange: OnFiltersChange) {
        this.container = container;
        this.onFiltersChange = onFiltersChange;
    }

    public bind(): void {
        const selects = this.container.querySelectorAll<HTMLSelectElement>('[data-edit-mode-filter="true"]');
        for (const select of selects) {
            select.addEventListener('change', () => this.collectAndNotify());
        }
    }

    public collectFilters(): FiltersRecord {
        const filters: FiltersRecord = {};
        const selects = this.container.querySelectorAll<HTMLSelectElement>('[data-edit-mode-filter="true"]');
        for (const select of selects) {
            const value = select.value.trim();
            if (value) {
                filters[select.name] = value;
            }
        }
        return filters;
    }

    private collectAndNotify(): void {
        this.onFiltersChange(this.collectFilters());
    }
}

export default FilterFormAjaxManager;
export type { FiltersRecord, OnFiltersChange };
