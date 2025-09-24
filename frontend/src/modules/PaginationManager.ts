class PaginationManager {
    private readonly DOMPagination: HTMLElement;
    private static readonly parameterName: string = 'page';

    
    constructor() {
        this.DOMPagination = document.getElementById('pagination') as HTMLElement;
    }

    public addEventListeners() {
        if (!this.DOMPagination) {
            return;
        }
        const paginationButtons = this.DOMPagination.querySelectorAll('.page-item');
        paginationButtons.forEach(pageItem => {
            if (pageItem.classList.contains('disabled')) {
                return;
            }
            const button = pageItem.querySelector('.page-link') as HTMLButtonElement;
            if (!button) return;
            
            button.addEventListener('click', (event) => {
                const target = event.target as HTMLElement;
                const page = target.dataset.page;
                if (page) {
                    this.changePage(Number.parseInt(page));
                }
            });
        });

    }

    private changePage(page: number) {
        const url = new URL(globalThis.location.href);
        url.searchParams.set(PaginationManager.getParameterName(), page.toString());
        globalThis.location.replace(url.toString());
    }

    public static getParameterName(): string {
        return this.parameterName;
    }

}

export {PaginationManager}