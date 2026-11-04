import BootstrapComponentInitializer from '@/modules/General/BootstrapComponentInitializer';

class FullScreen {
    hideAll: HTMLElement | null = null;
    showBaseLayoutButton: HTMLElement | null = null;

    constructor() {
        this.hideAll = document.getElementById('hideAll')
        this.showBaseLayoutButton = document.getElementById('showBaseLayoutButton');
    }

    public addEvent() {
        if (this.hideAll && this.showBaseLayoutButton) {
            this.hideAll.addEventListener('click', this.toggle);
            this.showBaseLayoutButton.addEventListener('click', this.toggle);
        }
    }

    private toggle() {
        const elementToToggles = document.getElementsByClassName('fullScreen-element');
        for (const element of Array.from(elementToToggles)) {
            element.classList.toggle('d-none');
        }
        const elementToTogglesInline = document.getElementsByClassName('fullScreen-element-inline');
        for (const element of Array.from(elementToTogglesInline)) {
            element.classList.toggle('d-inline');
        }
        const mainBody = document.getElementById('mainBody')
        if (mainBody) mainBody.classList.toggle('p-0');
        const mainContent = document.getElementById('main-content');
        if (mainContent) mainContent.classList.toggle('py-lg-5');

        setTimeout(() => {
            BootstrapComponentInitializer.hideAllTooltips();
        }, 30);
        setTimeout(() => {
            BootstrapComponentInitializer.hideAllTooltips();
        }, 50);
    }
}

export default FullScreen;
