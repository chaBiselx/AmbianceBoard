import { PaginationManager } from "@/modules/PaginationManager";

class TagManager {
    private readonly DOMTag: HTMLElement;

    
    constructor() {
        this.DOMTag = document.getElementById('tag-search') as HTMLElement;
    }

    public addEventListeners() {
        if (!this.DOMTag) {
            return;
        }
        for (const tagElement of this.DOMTag.querySelectorAll('.tag-element-redirect')) {
            tagElement.addEventListener('click', (event) => {
                const target = event.currentTarget as HTMLElement;
                const tag = target.dataset.tag;
                if (tag) {
                    this.changePage(tag);
                }
            });
        }

    }

    private changePage(tag: string) {
        const url = new URL(window.location.href);
        url.searchParams.set('tag', tag);
        url.searchParams.delete(PaginationManager.getParameterName()); // Remove the page parameter to reset pagination

        globalThis.location.replace(url.toString());
    }

}

export {TagManager}