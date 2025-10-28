import Notification from '@/modules/General/Notifications';
import ReportingContent from '@/modules/ReportingContent'
import { PaginationManager } from '@/modules/PaginationManager';
import { TagManager } from '@/modules/TagManager';
import * as bootstrap from 'bootstrap';
import ConsoleCustom from "@/modules/General/ConsoleCustom";
import ConsoleTesteur from "@/modules/General/ConsoleTesteur";
import Csrf from "@/modules/General/Csrf";
import GeneralTheme from "@/modules/General/GeneralTheme";
import Time from "@/modules/Util/Time";

// Gestionnaire global pour les erreurs de promesses non gérées
window.addEventListener('unhandledrejection', (event) => {
    console.error('Unhandled Promise Rejection', {
        reason: event.reason,
        promise: event.promise,
        message: event.reason?.message || String(event.reason),
        stack: event.reason?.stack,
        timestamp: Date.now(),
        url: window.location.href,
        userAgent: navigator.userAgent
    });
    
    // Vérifier si c'est l'erreur spécifique des extensions de navigateur
    if (event.reason?.message && 
        (event.reason.message.includes('message channel closed') || 
         event.reason.message.includes('asynchronous response'))) {
        console.error('Browser Extension Message Channel Error Detected', {
            errorMessage: event.reason.message,
            stack: event.reason.stack,
            timestamp: Date.now()
        });
        // Empêcher l'affichage de l'erreur dans la console si c'est lié aux extensions
        event.preventDefault();
    }
});

// Gestionnaire global pour les erreurs non capturées
window.addEventListener('error', (event) => {
    console.error('Uncaught Error', {
        message: event.message,
        filename: event.filename,
        lineno: event.lineno,
        colno: event.colno,
        error: event.error,
        stack: event.error?.stack,
        timestamp: Date.now(),
        url: window.location.href
    });
});


// Initialise automatiquement tous les composants Bootstrap disponibles
document.addEventListener('DOMContentLoaded', async () => {
    // Dropdown
    for (const element of document.querySelectorAll('[data-bs-toggle="dropdown"]')) {
        try {
            new bootstrap.Dropdown(element);
        } catch (error) {
            ConsoleCustom.warn(`Bootstrap Dropdown initialization failed: ${error}`);
        }
    }

    // Tooltip
    for (const element of document.querySelectorAll('[data-bs-toggle="tooltip"]')) {
        try {
            new bootstrap.Tooltip(element);
        } catch (error) {
            ConsoleCustom.warn(`Bootstrap Tooltip initialization failed: ${error}`);
        }
    }

    // Popover
    for (const element of document.querySelectorAll('[data-bs-toggle="popover"]')) {
        try {
            new bootstrap.Popover(element);
        } catch (error) {
            ConsoleCustom.warn(`Bootstrap Popover initialization failed: ${error}`);
        }
    }

    ConsoleTesteur.log('General Event initialised');
});


document.addEventListener("DOMContentLoaded", () => {
    new GeneralTheme().addEvent();
    new FullScreen().addEvent();
    new EmailConfirmationAccount('resend_email_confirmation_account').addEvent();
    new Sidebar().addEvent();
    new ReportingContent('reportButton').addEvent();
    new PaginationManager().addEventListeners();
    new TagManager().addEventListeners();
    new NotificationGeneral().addEvent();
    new DeleteAccount().addEvent();
    new UserActivityLog().addEvent();
    new ShowConsoleBetaTester().addEvent();

});

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
                    .then(data => {
                        Notification.createClientNotification({ message: 'Email envoyé avec success', type: 'success' })
                    })
                    .catch(error => {
                        console.error(error)
                        Notification.createClientNotification({ message: 'Une erreur est survenue', type: 'error' })
                    });
            }

        }


    }
}


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
    }
}

class Sidebar {
    sidebarToggle: HTMLButtonElement | null = null
    sidebar: HTMLDivElement | null = null

    constructor() {
        // Mobile sidebar toggle
        this.sidebarToggle = document.querySelector('.navbar-toggler');
        this.sidebar = document.querySelector('.sidebar');
    }

    public addEvent() {
        if (this.sidebarToggle && this.sidebar) {
            this.sidebarToggle.addEventListener('click', this.toggle.bind(this));
        }
    }
    public toggle() {
        if (this.sidebar) {
            this.sidebar.classList.toggle('d-block');
        }
    }

}

class NotificationGeneral {
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
                // .then(response => response.json())
                .then(_ => {

                })
                .catch(_ => {
                });
        }
    }
}

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
                            Notification.createClientNotification({ message: 'Une erreur est survenue', type: 'error' });
                        }
                    });
            }

        }
    }
}

class UserActivityLog {
    url: string | null = null;
    element: HTMLElement | null = null;
    constructor() {
        this.element = document.getElementById('trace_user_activity') || null;
    }

    private getUrl() {
        return this.element?.dataset.url || null;
    }

    public addEvent() {
        if (this.element) {
            // Détection de la fermeture volontaire de la page (fermeture onglet, navigation, rafraîchissement)
            window.addEventListener('beforeunload', () => {
                this.postActivityLog();
            });

            //envoyer toutes les 15 min en cas de coupure
            setInterval(() => {
                this.postActivityLog();
            }, Time.get_minutes(15));
        }
    }

    private postActivityLog() {
        const url = this.getUrl();
        if (url) {
            fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': Csrf.getToken()!
                },
            })
                .then(_response => {
                    // Log envoyé avec succès
                })
                .catch(error => {
                    console.error('There was a problem with the fetch operation:', error);
                });
        }
    }
}

class ShowConsoleBetaTester {
    buttonShow: HTMLButtonElement | null = null;
    consoleElement: HTMLElement | null = null;

    constructor() {
        this.buttonShow = document.getElementById('showLoggerBetaTest') as HTMLButtonElement;
        this.consoleElement = document.getElementById('betaTestConsole');
    }

    public addEvent() {
        if (this.buttonShow && this.consoleElement) {
            this.buttonShow.addEventListener('click', this.toggleConsole.bind(this));
        }
    }

    private toggleConsole() {
        if (this.consoleElement) {
            this.consoleElement.classList.toggle('d-none');
        }
    }
}