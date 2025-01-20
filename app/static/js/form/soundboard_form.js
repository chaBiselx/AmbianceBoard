simulateSoundBoardColor();

const DomElementAddEvent = ['id_name', 'id_color', 'id_colorText', 'id_icon'];
for (let i = 0; i < DomElementAddEvent.length; i++) {
    document.getElementById(DomElementAddEvent[i]).addEventListener('input', simulateSoundBoardColor);
    document.getElementById(DomElementAddEvent[i]).addEventListener('change', simulateSoundBoardColor);
}

function simulateSoundBoardColor() {
    const demo = document.getElementById('demo-soundboard')
    demo.style.backgroundColor = document.getElementById('id_color').value;
    demo.style.color = document.getElementById('id_colorText').value;

    if (document.getElementById('id_icon').value != "") {
        const reader = new FileReader();
        reader.addEventListener("load", () => {
            demo.innerHTML = "<img class='playlist-img' src=" + reader.result + " ></img>";
        });
        html =  reader.readAsDataURL(document.getElementById('id_icon').files[0]);
        if(html){
            demo.innerHTML = "<img class='playlist-img' src=" + html + " ></img>";
        }
    } else if(document.getElementById('id_icon_alreadyexist')){
        demo.innerHTML = "<img class='playlist-img' src=" + document.getElementById('id_icon_alreadyexist').href + " ></img>";
    } else {
        demo.textContent = document.getElementById('id_name').value;
    }

}

function confirmSuppression(el) {
    config = {};
    config.delete_url = el.dataset.deleteurl;
    config.redirect_url = el.dataset.redirecturl;

    if (confirm("Êtes-vous sûr de vouloir supprimer cet élément ?")) {
        callAjax(config)
    } else {
        // Annuler la suppression
    }
}

function callAjax(config) {
    var csrfToken = getCookie('csrftoken');
    fetch(config.delete_url, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken
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