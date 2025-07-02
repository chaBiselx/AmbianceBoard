import Cookie from "@/modules/Cookie";
import Notification from '@/modules/Notifications';
import ReportingContent from '@/modules/ReportingContent'
import * as bootstrap from 'bootstrap';

// Initialise automatiquement tous les composants Bootstrap disponibles
document.addEventListener('DOMContentLoaded', () => {
    // Dropdown
    document.querySelectorAll('[data-bs-toggle="dropdown"]').forEach(element => {
        try {
            new bootstrap.Dropdown(element);
        } catch (error) {
        }
    });

    // Tooltip
    document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(element => {
        try {
            new bootstrap.Tooltip(element);
        } catch (error) {
        }
    });

    // Popover
    document.querySelectorAll('[data-bs-toggle="popover"]').forEach(element => {
        try {
            new bootstrap.Popover(element);
        } catch (error) {
        }
    });
});


document.addEventListener("DOMContentLoaded", () => {
    new GeneralTheme().addEvent();
    new FullScreen().addEvent();
    new EmailConfirmationAccount('resend_email_confirmation_account').addEvent();
    new Sidebar().addEvent();
    new ReportingContent('reportButton').addEvent();


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
            const csrfToken = Cookie.get('csrftoken')!;
            if (url) {
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
        this.theme = localStorage.getItem('theme') ?? 'light';
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
        localStorage.setItem('theme', this.theme);


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
        const csrfToken = Cookie.get('csrftoken')!;

        if (url) {
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
