import Csrf from "@/modules/General/Csrf";
import ConsoleCustom from './modules/General/ConsoleCustom';

type deleteConfig = { delete_url: string, redirect_url: string };

class TagSelector {

    private readonly tagBadges: string = '.tag-badge'
    private readonly classSelected: string = 'badge-selected'
    private readonly classUnselected: string = 'badge-unselected'

    public init() {
        const tagBadges = document.querySelectorAll(this.tagBadges);

        tagBadges.forEach((badge) => {
            badge.addEventListener('click', (e) => {
                this.actionEvent(e);
            });
        });
    }

    private actionEvent(event: Event) {
        event.preventDefault();
        
        if (!event.target) return;
        
        let el = event.target as HTMLElement;
        const tagId = el.getAttribute('data-tag-id');
        
        if (!tagId) {
            ConsoleCustom.warn('Tag ID not found on element:', el);
            return;
        }
        
        const checkbox = document.getElementById('tag_' + tagId) as HTMLInputElement;
        
        if (!checkbox || checkbox.type !== "checkbox") {
            ConsoleCustom.warn('Checkbox not found or not a valid input element:', checkbox);
            return;
        }

        // Toggle le checkbox
        checkbox.checked = !checkbox.checked;
        
        // Met à jour l'apparence du badge (appliquer les classes sur le badge, pas sur le checkbox)
        if (checkbox.checked) {
            el.classList.remove(this.classUnselected);
            el.classList.add(this.classSelected);
        } else {
            el.classList.remove(this.classSelected);
            el.classList.add(this.classUnselected);
        }
    }



}

simulateSoundBoardColor();

const DomElementAddEventList = ['id_name', 'id_color', 'id_colorText', 'id_icon'];
for (const DomElementAddEvent of DomElementAddEventList) {
    const input = document.getElementById(DomElementAddEvent) as HTMLInputElement;
    input.addEventListener('input', simulateSoundBoardColor);
    input.addEventListener('change', simulateSoundBoardColor);
}
document.addEventListener('DOMContentLoaded', function () {
    (new TagSelector()).init();
})


function simulateSoundBoardColor() {
    const demo = document.getElementById('demo-soundboard') as HTMLDivElement;
    if (demo == null) {
        return
    }
    const color = document.getElementById('id_color') as HTMLInputElement;
    const colorText = document.getElementById('id_colorText') as HTMLInputElement;
    demo.style.backgroundColor = color.value;
    demo.style.color = colorText.value;

    const imgInput = document.getElementById('id_icon') as HTMLInputElement;
    if (imgInput.value != "") {
        const reader = new FileReader();
        reader.addEventListener("load", () => {
            demo.innerHTML = "<img class='playlist-img' src=" + reader.result + " ></img>";
        });
        if (imgInput.files?.[0]) {
            reader.readAsDataURL(imgInput.files[0])
        }
    } else if (document.getElementById('id_icon_alreadyexist')) {
        const urlImg = document.getElementById('id_icon_alreadyexist') as HTMLLinkElement;
        demo.innerHTML = "<img class='playlist-img' src=" + urlImg.href + " ></img>";
    } else {
        const inputName = document.getElementById('id_name') as HTMLInputElement;
        demo.textContent = inputName.value;
    }

}

document.addEventListener("DOMContentLoaded", () => {
    addDeleteSoundboardEvent();
});

function addDeleteSoundboardEvent() {
    const deletePlaylistBtn = document.getElementById('btn-delete-soundboard');
    if (deletePlaylistBtn) {
        deletePlaylistBtn.addEventListener('click', confirmSuppression);
    }
}

function confirmSuppression(event: Event) {
    const el = event.target as HTMLButtonElement;
    if (el.dataset.deleteurl && el.dataset.redirecturl) {
        const config: deleteConfig = {
            delete_url: el.dataset.deleteurl,
            redirect_url: el.dataset.redirecturl
        };

        if (confirm("Êtes-vous sûr de vouloir supprimer cet élément ?")) {
            callAjax(config, 'DELETE')
        } else {
            // Annuler la suppression
        }
    }
}

function callAjax(config: deleteConfig, method: string = 'POST') {
    fetch(config.delete_url, {
        method: method,
        headers: {
            'X-CSRFToken': Csrf.getToken()!
        },
    })
        .then(response => {
            if (response.status === 200) {
                window.location.href = config.redirect_url;
            } else {
                // Gestion des erreurs
                console.error('Erreur lors de la suppression');
            }
        })
        .catch(error => {
            ConsoleCustom.error('Erreur lors de la requête AJAX:', error);
        });
}

