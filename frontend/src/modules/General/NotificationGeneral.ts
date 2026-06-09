import Csrf from "@/modules/General/Csrf";

export default class NotificationGeneral {
    sectionMessage: HTMLElement | null = null;

    constructor() {
        this.sectionMessage = document.getElementById('notifications-general');
    }

    public addEvent() {
        if (this.sectionMessage) {
            const listCloseButton = this.sectionMessage.getElementsByClassName('close-notification') as HTMLCollectionOf<HTMLButtonElement>;
            for (const element of Array.from(listCloseButton)) {
                element.addEventListener('click', this.dismissNotification.bind(this));
            }
        }
    }

    private dismissNotification(event: Event) {
        const target = event.target as HTMLElement;
        if (target.classList.contains('close-notification')) {
            const alertElement = target.closest('.alert');
            if (alertElement) {
                alertElement.remove();
            }

            if (target.dataset.metaUrl_dismiss) {
                this.dismissNotificationFromServer(target.dataset.metaUrl_dismiss);
            }
        }
    }

    private dismissNotificationFromServer(url: string) {
        const csrfToken = Csrf.getToken();
        if (url && csrfToken) {
            fetch(url, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken
                },
            })
                .then(() => {
                })
                .catch(() => {
                });
        }
    }
}