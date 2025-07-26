import Notification from '@/modules/General/Notifications';
import ConsoleCustom from "@/modules/General/ConsoleCustom";


class ShareLinkManager {
    private shareButtons: NodeListOf<HTMLElement>;

    constructor() {
        this.shareButtons = document.querySelectorAll('.share-link-btn');
    }

    public addEvent() {
        this.shareButtons.forEach(button => {
            button.addEventListener('click', this.copyToClipboard.bind(this));
        });
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
        const textArea = document.createElement('textarea');
        textArea.value = text;
        textArea.style.position = 'fixed';
        textArea.style.left = '-999999px';
        textArea.style.top = '-999999px';
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        
        try {
            document.execCommand('copy');
            Notification.createClientNotification({ 
                message: 'Lien copié dans le presse-papiers', 
                type: 'success' 
            });
        } catch (error) {
            Notification.createClientNotification({ 
                message: 'Impossible de copier le lien', 
                type: 'error' 
            });
        }
        
        document.body.removeChild(textArea);
    }
}

export default ShareLinkManager;