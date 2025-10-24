import Notification from '@/modules/General/Notifications';
import ConsoleCustom from "@/modules/General/ConsoleCustom";


class ShareLinkManager {
    private readonly shareButtons: NodeListOf<HTMLElement>;

    constructor() {
        this.shareButtons = document.querySelectorAll('.share-link-btn');
    }

    public addEvent() {
        for (const button of this.shareButtons) {
            button.addEventListener('click', this.copyToClipboard.bind(this));
        }
    }

    private async copyToClipboard(event: Event) {
        event.preventDefault();

        const button = event.currentTarget as HTMLElement;
        const url = button.dataset.url || button.getAttribute('href');

        if (!url) {
            Notification.createClientNotification({
                message: 'URL non trouvée',
                type: 'error'
            });
            return;
        }

        try {
            await navigator.clipboard.writeText(url);

            Notification.createClientNotification({
                message: 'Lien copié dans le presse-papiers',
                type: 'success'
            });

        } catch (error) {
            ConsoleCustom.warn(`Erreur lors de la copie: ${error}`);

            // Fallback pour les navigateurs non compatibles
            this.fallbackCopyToClipboard(url);
        }
    }

    private fallbackCopyToClipboard(text: string) {
        navigator.clipboard.writeText(text).then(
            function () {
                Notification.createClientNotification({
                    message: 'Lien copié dans le presse-papiers',
                    type: 'success'
                });
            })
            .catch(
                function () {
                    Notification.createClientNotification({
                        message: 'Impossible de copier le lien',
                        type: 'error'
                    });
                });
    }
}

export default ShareLinkManager;