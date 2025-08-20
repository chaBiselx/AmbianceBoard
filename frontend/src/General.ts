import Notification from '@/modules/General/Notifications';
import ReportingContent from '@/modules/ReportingContent'
import { PaginationManager } from '@/modules/PaginationManager';
import { TagManager } from '@/modules/TagManager';
import * as bootstrap from 'bootstrap';
import ConsoleCustom from "./modules/General/ConsoleCustom";
import Csrf from "./modules/General/Csrf";
import Cookie from "@/modules/General/Cookie";
import Time from "@/modules/Util/Time";

// Initialise automatiquement tous les composants Bootstrap disponibles
document.addEventListener('DOMContentLoaded', () => {
    // Dropdown
    document.querySelectorAll('[data-bs-toggle="dropdown"]').forEach(element => {
        try {
            new bootstrap.Dropdown(element);
        } catch (error) {
            ConsoleCustom.warn(`Bootstrap Dropdown initialization failed: ${error}`);
        }
    });

    // Tooltip
    document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(element => {
        try {
            new bootstrap.Tooltip(element);
        } catch (error) {
            ConsoleCustom.warn(`Bootstrap Tooltip initialization failed: ${error}`);
        }
    });

    // Popover
    document.querySelectorAll('[data-bs-toggle="popover"]').forEach(element => {
        try {
            new bootstrap.Popover(element);
        } catch (error) {
            ConsoleCustom.warn(`Bootstrap Popover initialization failed: ${error}`);
        }
    });
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

class GeneralTheme {
    theme: string
    buttonToggle: HTMLButtonElement

    constructor() {
        this.theme = Cookie.get('theme') ?? 'light';
        this.buttonToggle = document.getElementById('darkModeToggle') as HTMLButtonElement;
        this.toggleIcon();
        this.toggleAttribute();


    }

    public addEvent() {
        if (this.buttonToggle) {
            this.buttonToggle.addEventListener('click', this.toggleTheme.bind(this));
        }
    }

    private toggleTheme() {
        this.theme = this.theme === 'light' ? 'dark' : 'light';
        this.toggleIcon();
        this.toggleAttribute();
        this.saveTheme();
        Cookie.set('theme', this.theme);
    }

    private toggleAttribute() {
        const htmlElement = document.documentElement;
        htmlElement.setAttribute('data-bs-theme', this.theme);
    }

    private toggleIcon() {
        if (this.theme === 'dark') {
            this.buttonToggle.innerHTML = `<i class="fa-solid fa-sun"></i>`;
        } else {
            this.buttonToggle.innerHTML = `<i class="fa-solid fa-moon"></i>`;
        }
    }

    private saveTheme() {
        const url = this.buttonToggle.dataset.url
        const csrfToken = Csrf.getToken();

        if (url && csrfToken) {
            fetch(url, {
                method: 'UPDATE',
                headers: {
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({ theme: this.theme })
            })
                .then(response => response.json())
                .then(data => {
                })
                .catch(error => {
                    console.error(error)
                });
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
        Array.from(elementToToggles).forEach(element => {
            element.classList.toggle('d-none');
        });
        const elementToTogglesInline = document.getElementsByClassName('fullScreen-element-inline');
        Array.from(elementToTogglesInline).forEach(element => {
            element.classList.toggle('d-inline');
        });
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
            Array.from(listCloseButton).forEach((element: HTMLButtonElement) => {
                element.addEventListener('click', this.dismissNotification.bind(this));
            });
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
    private deleteAccountButton: HTMLButtonElement | null = null;

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
                            window.location.href = '/';
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