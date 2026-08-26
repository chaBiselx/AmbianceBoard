import Notification from '@/modules/General/Notifications';
import Csrf from '@/modules/General/Csrf';
import { PlayerCustomFactory } from '@/modules/Audio/PlayerCustom';

document.addEventListener('DOMContentLoaded', () => {
    new PlaylistProposalsManagement().addEvent();
    PlayerCustomFactory.create();
});

class PlaylistProposalsManagement {

    public addEvent(): void {
        const buttons = document.querySelectorAll('.proposal-accept-btn, .proposal-refuse-btn');
        for (const button of buttons) {
            if (!(button instanceof HTMLButtonElement)) continue;
            button.addEventListener('click', () => this.callAction(button));
        }
    }

    private callAction(button: HTMLButtonElement): void {
        const url = button.dataset.url;
        if (!url) return;

        button.setAttribute('disabled', 'true');
        fetch(url, {
            method: 'POST',
            headers: {
                'X-CSRFToken': Csrf.getToken()!,
            },
        })
            .then(async (response) => {
                const data = await response.json();
                return { data, ok: response.ok };
            })
            .then(({ data, ok }) => {
                if (ok && data.success) {
                    Notification.createClientNotification({ message: data.message || 'Action effectuée', type: 'success' });
                    const card = button.closest('[id^="proposal-card-"]');
                    card?.remove();
                } else {
                    Notification.createClientNotification({ message: data.error || 'Une erreur est survenue', type: 'error' });
                    button.removeAttribute('disabled');
                }
            })
            .catch(() => {
                Notification.createClientNotification({ message: 'Une erreur est survenue', type: 'error' });
                button.removeAttribute('disabled');
            });
    }
}
