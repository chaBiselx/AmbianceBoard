type TrackLabelReportModalOptions = {
    title: string;
    body: string;
    footer: string;
    width: string;
    callback?: () => void;
};

export type TrackLabelReportDependencies = {
    fetch: typeof fetch;
    getCsrfToken: () => string | null;
    showModal: (options: TrackLabelReportModalOptions) => void;
    hideModal: () => void;
    notify: (message: string, type: 'success' | 'danger') => void;
};

export class TrackLabelReport {
    constructor(
        private readonly dependencies: TrackLabelReportDependencies,
        private readonly doc: Document = document,
    ) {}

    initialize(): void {
        for (const button of this.doc.querySelectorAll<HTMLButtonElement>('.btn-report-track-labels')) {
            button.addEventListener('click', () => this.openReportModal(button));
        }
    }

    private openReportModal(button: HTMLButtonElement): void {
        const track = button.closest<HTMLElement>('.music');
        const url = button.dataset.url;
        const labels = track?.querySelectorAll<HTMLElement>('.track-label');
        if (!track || !url || !labels?.length) return;

        const form = this.createReportForm(labels, button);
        this.dependencies.showModal({
            title: button.dataset.modalTitle ?? '',
            body: form.outerHTML,
            footer: '',
            width: 'md',
            callback: () => {
                const modalForm = this.doc.querySelector<HTMLFormElement>('.track-label-report-form');
                modalForm?.addEventListener('submit', event => {
                    event.preventDefault();
                    void this.submitReport(modalForm, url, button);
                });
                this.doc.querySelector<HTMLButtonElement>('.track-label-report-cancel')?.addEventListener('click', () => {
                    this.dependencies.hideModal();
                });
            },
        });
    }

    private createReportForm(labels: NodeListOf<HTMLElement>, button: HTMLButtonElement): HTMLFormElement {
        const form = this.doc.createElement('form');
        form.className = 'track-label-report-form';
        form.append(
            this.createDescription(button),
            this.createLabelList(labels),
            this.createErrorMessage(button),
            this.createActions(button),
        );
        return form;
    }

    private createDescription(button: HTMLButtonElement): HTMLParagraphElement {
        const description = this.doc.createElement('p');
        description.textContent = button.dataset.modalDescription ?? '';
        return description;
    }

    private createLabelList(labels: NodeListOf<HTMLElement>): HTMLDivElement {
        const list = this.doc.createElement('div');
        list.className = 'd-flex flex-column gap-2';
        labels.forEach(label => list.appendChild(this.createLabelOption(label)));
        return list;
    }

    private createLabelOption(label: HTMLElement): HTMLLabelElement {
        const labelElement = this.doc.createElement('label');
        labelElement.className = 'form-check d-flex align-items-center gap-2';

        const input = this.doc.createElement('input');
        input.className = 'form-check-input m-0';
        input.type = 'checkbox';
        input.name = 'label_ids';
        input.value = label.dataset.labelId ?? '';

        const text = this.doc.createElement('span');
        const confidence = Number.parseFloat(label.dataset.confidence ?? '0');
        const confidenceText = Number.isFinite(confidence) ? ` (${Math.round(confidence * 100)}%)` : '';
        text.textContent = `${label.dataset.label ?? label.textContent?.trim() ?? ''} · ${confidenceText}`;

        labelElement.append(input, text);
        return labelElement;
    }

    private createErrorMessage(button: HTMLButtonElement): HTMLParagraphElement {
        const error = this.doc.createElement('p');
        error.className = 'track-label-report-error text-danger mt-2 d-none';
        error.setAttribute('role', 'alert');
        error.textContent = button.dataset.modalEmpty ?? '';
        return error;
    }

    private createActions(button: HTMLButtonElement): HTMLDivElement {
        const actions = this.doc.createElement('div');
        actions.className = 'd-flex justify-content-end gap-2 mt-3';

        const cancel = this.doc.createElement('button');
        cancel.type = 'button';
        cancel.className = 'btn btn-secondary track-label-report-cancel';
        cancel.textContent = button.dataset.modalCancel ?? '';

        const submit = this.doc.createElement('button');
        submit.type = 'submit';
        submit.className = 'btn btn-primary';
        submit.textContent = button.dataset.modalSubmit ?? '';

        actions.append(cancel, submit);
        return actions;
    }

    private async submitReport(form: HTMLFormElement, url: string, button: HTMLButtonElement): Promise<void> {
        const selected = form.querySelectorAll<HTMLInputElement>('input[name="label_ids"]:checked');
        const error = form.querySelector<HTMLElement>('.track-label-report-error');
        if (!selected.length) {
            error?.classList.remove('d-none');
            return;
        }

        const csrfToken = this.dependencies.getCsrfToken();
        if (!csrfToken) {
            this.dependencies.notify(button.dataset.modalError ?? '', 'danger');
            return;
        }

        const payload = new URLSearchParams();
        selected.forEach(input => payload.append('label_ids', input.value));
        const submit = form.querySelector<HTMLButtonElement>('button[type="submit"]');
        if (submit) submit.disabled = true;

        try {
            const response = await this.dependencies.fetch(url, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken,
                    'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
                },
                body: payload.toString(),
            });
            const result = await response.json() as { success?: boolean };
            if (!response.ok || !result.success) throw new Error('Report submission failed');

            this.dependencies.hideModal();
            this.dependencies.notify(button.dataset.modalSuccess ?? '', 'success');
        } catch {
            this.dependencies.notify(button.dataset.modalError ?? '', 'danger');
            if (submit) submit.disabled = false;
        }
    }
}

export function initializeTrackLabelReport(
    dependencies: TrackLabelReportDependencies,
    doc: Document = document,
): void {
    new TrackLabelReport(dependencies, doc).initialize();
}
