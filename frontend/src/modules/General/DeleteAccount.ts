import Notification from '@/modules/General/Notifications';
import ConsoleTraceServeur from '@/modules/General/ConsoleTraceServeur';
import Csrf from '@/modules/General/Csrf';

class DeleteAccount {
    private readonly deleteAccountButton: HTMLButtonElement | null = null;

    constructor() {
        this.deleteAccountButton = document.getElementById('delete-account') as HTMLButtonElement;
    }

    public addEvent() {
        if (this.deleteAccountButton) {
            this.deleteAccountButton.addEventListener('click', this.confirmDelete.bind(this));
        }
    }

    private confirmDelete(event: Event) {
        event.preventDefault();
        if (confirm("Êtes-vous sûr de vouloir supprimer votre compte ? Cette action est irréversible.")) {
            const method = this.deleteAccountButton?.closest('form')?.attributes.getNamedItem('method')?.value;
            const url = this.deleteAccountButton?.closest('form')?.action;
            if (method && url) {
                fetch(url, {
                    method: method,
                    headers: {
                        'X-CSRFToken': Csrf.getToken()!
                    }
                })
                    .then(response => {
                        if (response.ok) {
                            globalThis.location.href = '/';
                        } else {
                            Notification.createClientNotification({ message: 'Une erreur est survenue', type: 'danger' });
                        }
                    })
                    .catch((error) => {
                        ConsoleTraceServeur.error('Failed to delete account:', error);
                    });
            }
        }
    }
}

export default DeleteAccount;
