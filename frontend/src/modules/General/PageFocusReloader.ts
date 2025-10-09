
class PageFocusReloader {
    public setupFocusListener(): void {
        window.addEventListener('focus', () => {
            globalThis.location.reload();
        });
    }
}

export default PageFocusReloader;