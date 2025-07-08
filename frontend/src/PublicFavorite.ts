import Csrf from "./modules/Csrf";


document.addEventListener("DOMContentLoaded", () => {
    const listFavoriteAction = document.getElementsByClassName('favorite-action');
    if (listFavoriteAction) {
        for (const favoriteActionElement of listFavoriteAction) {
            const favoriteAction = new PublicFavorite(favoriteActionElement as HTMLInputElement);
            favoriteAction.addEvent();
        }
    }
});



class PublicFavorite {
    element : HTMLInputElement
    url : string
    
    constructor(el: HTMLInputElement) {
        this.element = el
        this.url = el.dataset.url!
    }

    public addEvent() {
        this.element.addEventListener('click', this.toggle.bind(this))
    }

    private toggle() {
        this.saveData();
    }

    private saveData() {
        let method = 'POST';
        if(!this.element.checked){// invert because input already checked before event
            method = 'DELETE';
        }
        console.log(Csrf.getToken());
        
        fetch(this.url, {
            method: method,
            headers: {
                'X-CSRFToken': Csrf.getToken()!,
            },
        })

    }


}