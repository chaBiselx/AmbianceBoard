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
        this.DOMTag.querySelectorAll('.tag-element-redirect').forEach(tagElement => {
            tagElement.addEventListener('click', (event) => {
                const target = event.currentTarget as HTMLElement;
                const tag = target.dataset.tag;
                if (tag) {
                    this.changePage(tag);
                }
            });
        });

    }

    private changePage(tag: string) {
        const url = new URL(globalThis.location.href);
        url.searchParams.set('tag', tag);
        url.searchParams.delete(PaginationManager.getParameterName()); // Remove the page parameter to reset pagination

        window.location.replace(url.toString());
    }

}

export {TagManager}