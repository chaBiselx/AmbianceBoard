function toggleSidebar() {
    const sidebar = document.querySelector('.sidebar');
    const mainContent = document.querySelector('.main-content');
    sidebar.classList.toggle('hidden');
    mainContent.classList.toggle('full-width');
}

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function resentEmailConfirmation(el){
    el.style.display = 'none'
    url = el.dataset.url
    var csrfToken = getCookie('csrftoken');
    fetch(url, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken
        },
    })
        .then(response => response.json())
        .then(data => {
            createClientNotification({message: 'Email envoyé avec success', type: 'success'})
        })
        .catch(error => {
            console.error(error)
            createClientNotification({message: 'Une erreur est survenue', type: 'error'})
        });
}