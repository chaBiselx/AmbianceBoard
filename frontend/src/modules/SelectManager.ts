import { PaginationManager } from "@/modules/PaginationManager";


// TODO add heritage with TagSelector
class SelectManager {
    private readonly DOMTag: NodeListOf<HTMLElement>;


    constructor() {
        this.DOMTag = document.querySelectorAll('.dynamic-filter-search');
    }

    public addEventListeners() {
        if (!this.DOMTag) {
            return;
        }
        this.DOMTag.forEach(form => {
            
            for (const selectElement of form.querySelectorAll('.select-element-redirect')) {
                selectElement.addEventListener('change', (event) => {
                    const target = event.currentTarget as HTMLSelectElement;
                    const value = target.value ?? '';
                    this.changePage(value, target.name);
                });
            }
        });


    }

    private changePage(value: string, name: string) {
        const url = new URL(globalThis.location.href);
        url.searchParams.set(name, value);
        url.searchParams.delete(PaginationManager.getParameterName()); // Remove the page parameter to reset pagination

        globalThis.location.replace(url.toString());
    }

}

export { SelectManager }