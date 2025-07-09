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
            const button = pageItem.querySelector('.page-link') as HTMLButtonElement;
            if(button.classList.contains('disabled')) return;
            button.addEventListener('click', (event) => {
                const target = event.target as HTMLElement;
                const page = target.dataset.page;
                if (page) {
                    this.changePage(parseInt(page));
                }
            });
        });

    }

    private changePage(page: number) {
        const url = new URL(window.location.href);
        url.searchParams.set(PaginationManager.getParameterName(), page.toString());
        window.location.replace(url.toString());
    }

    public static getParameterName(): string {
        return this.parameterName;
    }

}

export {PaginationManager}