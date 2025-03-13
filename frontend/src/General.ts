import Cookie from "./modules/Cookie";
import Notification from './modules/Notifications';

document.addEventListener("DOMContentLoaded", () => {
    new EmailConfirmationAccount('resend_email_confirmation_account').addEvent();

});

class EmailConfirmationAccount {
    element: HTMLButtonElement| null = null

    constructor(idBtn : string){
        const element = document.getElementById(idBtn)
        if(element){
            this.element = element as HTMLButtonElement;
        }
    }

    public addEvent(){
        if(this.element){
            this.element.addEventListener('click', this.resentEmailConfirmation.bind(this));
        }

    }
    private resentEmailConfirmation(){
        if(this.element){
            this.element.style.display = 'none'
            const url = this.element.dataset.url
            const csrfToken = Cookie.get('csrftoken')!;
            if(url){
                fetch(url, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': csrfToken
                    },
                })
                    .then(response => response.json())
                    .then(data => {
                        Notification.createClientNotification({message: 'Email envoyé avec success', type: 'success'})
                    })
                    .catch(error => {
                        console.error(error)
                        Notification.createClientNotification({message: 'Une erreur est survenue', type: 'error'})
                    });
            }
            
        }

      
    }
}

