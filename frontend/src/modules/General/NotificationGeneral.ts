import Csrf from "@/modules/General/Csrf";

export default class NotificationGeneral {
    private static readonly DISMISSED_NOTIFICATIONS_COOKIE = 'dismissed_general_notifications';
    private static readonly DISMISSED_NOTIFICATIONS_COOKIE_TTL_DAYS = 30;

    sectionMessage: HTMLElement | null = null;

    constructor() {
        this.sectionMessage = document.getElementById('notifications-general');
    }

    /**
     * Initialise les evenements de fermeture sur les notifications.
     * Masque aussi les notifications deja fermeees pour les visiteurs anonymes.
     */
    public addEvent() {
        if (this.sectionMessage) {
            const listCloseButton = this.sectionMessage.getElementsByClassName('close-notification') as HTMLCollectionOf<HTMLButtonElement>;
            for (const element of Array.from(listCloseButton)) {
                this.hideIfDismissedForAnonymousUser(element);
                element.addEventListener('click', this.dismissNotification.bind(this));
            }
        }
    }

    /**
     * Gere la fermeture d'une notification cote client.
     * Pour un utilisateur connecte, delegue la persistence au serveur.
     * Pour un utilisateur anonyme, persiste l'identifiant dans un cookie.
     *
     * @param event Evenement click du bouton de fermeture.
     */
    private dismissNotification(event: Event) {
        const target = event.target as HTMLElement;
        if (target.classList.contains('close-notification')) {
            const alertElement = target.closest('.alert');
            if (alertElement) {
                alertElement.remove();
            }

            if (target.dataset.metaUrl_dismiss) {
                this.dismissNotificationFromServer(target.dataset.metaUrl_dismiss);
                return;
            }

            const notificationUuid = target.dataset.metaUuid;
            if (notificationUuid) {
                this.saveDismissedNotificationToCookie(notificationUuid);
            }
        }
    }

    /**
     * Masque la notification si elle a deja ete fermee par un utilisateur anonyme.
     * Ignore le cas authentifie (pilotage serveur).
     *
     * @param closeButton Bouton de fermeture associe a l'alerte.
     */
    private hideIfDismissedForAnonymousUser(closeButton: HTMLButtonElement) {
        if (closeButton.dataset.metaUrl_dismiss) {
            return;
        }

        const notificationUuid = closeButton.dataset.metaUuid;
        if (!notificationUuid) {
            return;
        }

        const dismissedNotifications = this.getDismissedNotificationsFromCookie();
        if (dismissedNotifications.includes(notificationUuid)) {
            const alertElement = closeButton.closest('.alert');
            if (alertElement) {
                alertElement.remove();
            }
        }
    }

    /**
     * Ajoute un UUID de notification fermee dans le cookie local,
     * sans dupliquer une valeur deja presente.
     *
     * @param notificationUuid UUID unique de la notification.
     */
    private saveDismissedNotificationToCookie(notificationUuid: string) {
        const dismissedNotifications = this.getDismissedNotificationsFromCookie();
        if (dismissedNotifications.includes(notificationUuid)) {
            return;
        }

        dismissedNotifications.push(notificationUuid);
        this.writeDismissedNotificationsCookie(dismissedNotifications);
    }

    /**
     * Lit la liste des notifications fermees dans le cookie.
     * Retourne un tableau vide si le cookie est absent ou invalide.
     */
    private getDismissedNotificationsFromCookie(): string[] {
        const cookieValue = this.getCookieValue(NotificationGeneral.DISMISSED_NOTIFICATIONS_COOKIE);
        if (!cookieValue) {
            return [];
        }

        try {
            const parsedValue: unknown = JSON.parse(decodeURIComponent(cookieValue));
            if (Array.isArray(parsedValue)) {
                return parsedValue.filter((value): value is string => typeof value === 'string');
            }
        } catch {
            return [];
        }

        return [];
    }

    /**
     * Ecrit la liste des UUID fermes dans un cookie JSON avec une date d'expiration.
     *
     * @param notificationUuids Liste des UUID a stocker.
     */
    private writeDismissedNotificationsCookie(notificationUuids: string[]) {
        const expires = new Date();
        expires.setDate(expires.getDate() + NotificationGeneral.DISMISSED_NOTIFICATIONS_COOKIE_TTL_DAYS);

        const cookieValue = encodeURIComponent(JSON.stringify(notificationUuids));
        document.cookie = `${NotificationGeneral.DISMISSED_NOTIFICATIONS_COOKIE}=${cookieValue}; expires=${expires.toUTCString()}; path=/; SameSite=Lax`;
    }

    /**
     * Recupere la valeur brute d'un cookie par son nom.
     *
     * @param name Nom du cookie.
     */
    private getCookieValue(name: string): string | null {
        const prefix = `${name}=`;
        const cookies = document.cookie ? document.cookie.split('; ') : [];

        for (const cookie of cookies) {
            if (cookie.startsWith(prefix)) {
                return cookie.substring(prefix.length);
            }
        }

        return null;
    }

    /**
     * Enregistre la fermeture d'une notification cote serveur.
     * Utilise un POST protege par token CSRF.
     *
     * @param url Endpoint de dismissal expose par le backend.
     */
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