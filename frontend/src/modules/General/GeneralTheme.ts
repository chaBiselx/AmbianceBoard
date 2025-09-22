import Cookie from "@/modules/General/Cookie";
import Csrf from "@/modules/General/Csrf";
import ConsoleTesteur from "@/modules/General/ConsoleTesteur";



class GeneralTheme {
    theme: string
    buttonToggle: HTMLButtonElement

    constructor() {
        this.theme = Cookie.get('theme') ?? 'light';
        ConsoleTesteur.log(`Theme from Cookie: ${this.theme}`);
        
        this.buttonToggle = document.getElementById('darkModeToggle') as HTMLButtonElement;
        ConsoleTesteur.log(`Button Toggle Element: ${this.buttonToggle.innerHTML.trim()}`);
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
        ConsoleTesteur.log(`Set Theme cookie: ${this.theme}`);

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
        ConsoleTesteur.log(`Set Theme backend: ${this.theme}`);

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
                    ConsoleTesteur.log(`Backend response : ${JSON.stringify(data)}`);

                })
                .catch(error => {
                    console.error(error)
                });
        }
    }

}

export default GeneralTheme;