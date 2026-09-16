import { PaginationManager } from "@/modules/PaginationManager";

class TagManager {
    private readonly DOMTag: NodeListOf<HTMLElement>;


    constructor() {
        this.DOMTag = document.querySelectorAll('.dynamic-filter-search');
    }

    public addEventListeners() {
        if (!this.DOMTag) {
            return;
        }
        this.DOMTag.forEach(form => {
            for (const tagElement of form.querySelectorAll('.tag-element-redirect')) {
                tagElement.addEventListener('click', (event) => {
                    const target = event.currentTarget as HTMLElement;
                    const tag = target.dataset.tag;
                    if (tag) {
                        this.changePage(tag);
                    }
                });
            }
        });


    }

    private changePage(tag: string) {
        const url = new URL(globalThis.location.href);
        url.searchParams.set('tag', tag);
        url.searchParams.delete(PaginationManager.getParameterName()); // Remove the page parameter to reset pagination

        globalThis.location.replace(url.toString());
    }

}

export { TagManager }