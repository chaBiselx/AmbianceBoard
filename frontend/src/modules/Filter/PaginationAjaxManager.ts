type OnPageChange = (page: number) => void;

/**
 * Gère la pagination AJAX dans un conteneur dynamique (modal, panel).
 * Cible les boutons #pagination .page-item et appelle le callback
 * avec le numéro de page lors du clic.
 */
class PaginationAjaxManager {
    private readonly container: HTMLElement;
    private readonly onPageChange: OnPageChange;

    constructor(container: HTMLElement, onPageChange: OnPageChange) {
        this.container = container;
        this.onPageChange = onPageChange;
    }

    public bind(): void {
        const pageItems = this.container.querySelectorAll('#pagination .page-item');
        for (const pageItem of pageItems) {
            if (pageItem.classList.contains('disabled')) continue;
            const button = pageItem.querySelector<HTMLButtonElement>('.page-link');
            if (!button) continue;
            button.addEventListener('click', (event) => {
                const page = (event.target as HTMLElement).dataset.page;
                if (page) {
                    this.onPageChange(Number.parseInt(page, 10));
                }
            });
        }
    }
}

export default PaginationAjaxManager;
export type { OnPageChange };
