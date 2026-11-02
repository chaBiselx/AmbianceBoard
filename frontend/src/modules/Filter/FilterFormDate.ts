class FilterFormDate {
    public init(): void {
        console.debug('Initializing FilterFormDate...');
        const forms = document.querySelectorAll<HTMLFormElement>('form[data-filter-form]');
        console.debug(`Found ${forms.length} forms with data-filter-date-range attribute.`);
        for (const form of forms) {
        console.debug(`Found ${forms.length} forms with data-filter-date-range attribute.`);

            this.bindDateInputs(form);
        }
    }

    private bindDateInputs(form: HTMLFormElement): void {
        const inputs = form.querySelectorAll<HTMLInputElement>('input[type="date"][data-filter-date-range]');
        for (const input of inputs) {
            input.addEventListener('change', () => form.submit());
        }
    }
}

export default FilterFormDate;
