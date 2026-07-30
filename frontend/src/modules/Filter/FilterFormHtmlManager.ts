/**
 * Gère la soumission automatique des formulaires de filtre.
 * Sélectionne les <form data-filter-form> dans le DOM et y attache :
 *   - les <select data-filter-select> : soumission au changement
 *   - les <input type="text"> : soumission à la touche Entrée
 */
class FilterFormHtmlManager {
    public init(): void {
        const forms = document.querySelectorAll<HTMLFormElement>('form[data-filter-form]');
        for (const form of forms) {
            this.bindSelects(form);
            this.bindTextInputs(form);
        }
    }

    private bindSelects(form: HTMLFormElement): void {
        const selects = form.querySelectorAll<HTMLSelectElement>('select[data-filter-select]');
        for (const select of selects) {
            select.addEventListener('change', () => form.submit());
        }
    }

    private bindTextInputs(form: HTMLFormElement): void {
        const inputs = form.querySelectorAll<HTMLInputElement>('input[type="text"], input[type="search"]');
        for (const input of inputs) {
            input.addEventListener('keydown', (event: KeyboardEvent) => {
                if (event.key === 'Enter') {
                    event.preventDefault();
                    form.submit();
                }
            });
        }
    }
}

export default FilterFormHtmlManager;
