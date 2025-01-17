

document.addEventListener("DOMContentLoaded", (event) => {
    setEventDragAndDrop()
    checkEmptyPlaylist()
});

function setEventDragAndDrop() {
    // Sélectionner les éléments HTML
    const playlistNonAssociees = document.getElementById('unassociated-playlists');
    const playlistAssociees = document.getElementById('associated-playlists');

    // Définir les événements de drag and drop
    playlistAssociees.addEventListener('dragstart', (e) => {
        e.dataTransfer.setData('id', e.target.id);
        e.dataTransfer.setData('dragstart', 'playlistAssociees');
    });

    playlistAssociees.addEventListener('dragover', (e) => {
        e.preventDefault();
    });

    playlistAssociees.addEventListener('drop', (e) => {
        e.preventDefault();
        dragstart = e.dataTransfer.getData('dragstart');
        if(dragstart == 'playlistAssociees') {
            return 
        }
        const id = e.dataTransfer.getData('id');
        const playlist = document.getElementById(id);
        playlistAssociees.appendChild(playlist);
        checkEmptyPlaylist();
        addMusic(playlist.id);
    });


    playlistNonAssociees.addEventListener('dragstart', (e) => {
        e.dataTransfer.setData('id', e.target.id);
        e.dataTransfer.setData('dragstart', 'playlistNonAssociees');
    });


    playlistNonAssociees.addEventListener('dragover', (e) => {
        e.preventDefault();
    });

    playlistNonAssociees.addEventListener('drop', (e) => {
        e.preventDefault();
        dragstart = e.dataTransfer.getData('dragstart');
        if(dragstart == 'playlistNonAssociees') {
            return 
        }
        const id = e.dataTransfer.getData('id');
        const playlist = document.getElementById(id);
        playlistNonAssociees.appendChild(playlist);
        checkEmptyPlaylist();
        removeMusic(playlist.id);
    });
}

function checkEmptyPlaylist() {
    const associatedPlaylists = document.getElementById('associated-playlists');
    const associatedNodesElement = associatedPlaylists.getElementsByClassName('playlist-dragAndDrop');
    const associatedPlaylistsEmpty = document.getElementsByClassName('associated-playlists-empty')[0];
    if (associatedNodesElement.length == 0) {
        associatedPlaylistsEmpty.removeAttribute('hidden');
    } else {
        associatedPlaylistsEmpty.setAttribute('hidden', 'true');
    }

    const unassociatedPlaylists = document.getElementById('unassociated-playlists');
    const unassociatedNodesElement = unassociatedPlaylists.getElementsByClassName('playlist-dragAndDrop');
    const unassociatedPlaylistsEmpty = document.getElementsByClassName('unassociated-playlists-empty')[0];
    if (unassociatedNodesElement.length == 0) {
        unassociatedPlaylistsEmpty.removeAttribute('hidden');
    } else {
        unassociatedPlaylistsEmpty.setAttribute('hidden', 'true');
    }
}



// Fonctions pour ajouter et supprimer des musiques
function addMusic(idPlaylist) {
    const associatedPlaylists = document.getElementById('associated-playlists');
    const url = associatedPlaylists.dataset.url;
    var csrfToken = getCookie('csrftoken');
    fetch(url, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            idPlaylist: idPlaylist,
        })
    })
        .then(response => response.json())
        .then(data => console.log(data))
        .catch(error => console.error(error));

}

function removeMusic(idPlaylist) {
    const associatedPlaylists = document.getElementById('associated-playlists');
    const url = associatedPlaylists.dataset.url;
    var csrfToken = getCookie('csrftoken');
    fetch(url, {
        method: 'DELETE',
        headers: {
            'X-CSRFToken': csrfToken,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            idPlaylist: idPlaylist,
        })
    })
        .then(response => response.json())
        .then(data => console.log(data))
        .catch(error => console.error(error));
}