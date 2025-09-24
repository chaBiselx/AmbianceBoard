import Cookie from "@/modules/General/Cookie";
import Csrf from "@/modules/General/Csrf";
import Boolean from "@/modules/Util/Boolean";



class GeneralTheme {
    theme: string
    buttonToggle: HTMLButtonElement

    constructor() {
    
        
        this.buttonToggle = document.getElementById('darkModeToggle') as HTMLButtonElement;
        if(this.buttonToggle.dataset?.backendSaved && Boolean.convert(this.buttonToggle.dataset?.backendSaved)){ // by User Preference
            this.theme = this.getHtmlAttribute() ?? 'light';
            Cookie.set('theme', this.theme);
        }else{// By Cookie
            this.theme = Cookie.get('theme') ?? 'light';
        }
    

        this.toggleIcon();
        this.toggleHtmlAttribute();


    }

    public addEvent() {
        if (this.buttonToggle) {
            this.buttonToggle.addEventListener('click', this.toggleTheme.bind(this));
        }
    }

    private toggleTheme() {
        this.theme = this.theme === 'light' ? 'dark' : 'light';
        this.toggleIcon();
        this.toggleHtmlAttribute();
        this.saveTheme();
        Cookie.set('theme', this.theme);

    }

    private toggleHtmlAttribute() {
        const htmlElement = document.documentElement as HTMLElement;
        (htmlElement.dataset as DOMStringMap).bsTheme = this.theme;
    }

    private getHtmlAttribute(): string | null {
        return document.documentElement.dataset.bsTheme ?? null;
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
                .then(_data => {
                })
                .catch(error => {
                    console.error(error)
                });
        }
    }

}

export default GeneralTheme;