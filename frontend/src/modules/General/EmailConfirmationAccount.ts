import Notification from '@/modules/General/Notifications';
import Csrf from '@/modules/General/Csrf';

class EmailConfirmationAccount {
    element: HTMLButtonElement | null = null

    constructor(idBtn: string) {
        const element = document.getElementById(idBtn)
        if (element) {
            this.element = element as HTMLButtonElement;
        }
    }

    public addEvent() {
        if (this.element) {
            this.element.addEventListener('click', this.resentEmailConfirmation.bind(this));
        }
    }

    private resentEmailConfirmation() {
        if (this.element) {
            this.element.style.display = 'none'
            const url = this.element.dataset.url
            const csrfToken = Csrf.getToken();
            if (url && csrfToken) {
                fetch(url, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': csrfToken
                    },
                })
                    .then(response => response.json())
                    .then(() => {
                        Notification.createClientNotification({ message: 'Email envoyé avec success', type: 'success' })
                    })
                    .catch(error => {
                        console.error(error)
                        Notification.createClientNotification({ message: 'Une erreur est survenue', type: 'danger' })
                    });
            }
        }
    }
}

export default EmailConfirmationAccount;
