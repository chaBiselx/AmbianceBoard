import Cookie from "@/modules/Cookie";

type deleteConfig = { delete_url: string, redirect_url: string };

simulateSoundBoardColor();

const DomElementAddEventList = ['id_name', 'id_color', 'id_colorText', 'id_icon'];
for (const DomElementAddEvent of DomElementAddEventList) {
    const input = document.getElementById(DomElementAddEvent) as HTMLInputElement;
    input.addEventListener('input', simulateSoundBoardColor);
    input.addEventListener('change', simulateSoundBoardColor);
}


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
    } else if(document.getElementById('id_icon_alreadyexist')){
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
    if(el.dataset.deleteurl && el.dataset.redirecturl){
        const config:deleteConfig = {
            delete_url:el.dataset.deleteurl,
            redirect_url:el.dataset.redirecturl
        };
    
        if (confirm("Êtes-vous sûr de vouloir supprimer cet élément ?")) {
            callAjax(config, 'DELETE')
        } else {
            // Annuler la suppression
        }
    }
}

function callAjax(config:deleteConfig, method: string = 'POST') {
    fetch(config.delete_url, {
        method: method,
        headers: {
            'X-CSRFToken': Cookie.get('csrftoken')!
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
            console.error('Erreur lors de la requête AJAX:', error);
        });
}