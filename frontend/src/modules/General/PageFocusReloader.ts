
class PageFocusReloader {
    constructor() {
        this.setupFocusListener();
    }

    private setupFocusListener(): void {
        window.addEventListener('focus', () => {
            window.location.reload();
        });
    }
}

export default PageFocusReloader;