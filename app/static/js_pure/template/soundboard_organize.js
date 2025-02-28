

document.addEventListener("DOMContentLoaded", (event) => {
    setEventDragAndDrop()
    checkEmptyPlaylist()
    initOrderBadge()
});

class DropPointHandler {
    constructor(playlist, children) {
        this.playlist = playlist;
        this.children = children;
        this.newOrder = null;
    }

    getDropPoint(e) {
        return {
            x: e.clientX,
            y: e.clientY
        };
    }

    getNewOrder() {
        return this.newOrder;
    }

    findClosestElement(dropPoint) {
        let closestElement = null;
        let closestDistance = Infinity;
        let insertAfter = false;

        this.children.forEach((child) => {
            if (child === this.playlist) return;

            const rect = child.getBoundingClientRect();
            const childCenter = {
                x: rect.left + rect.width / 2,
                y: rect.top + rect.height / 2
            };

            const distance = Math.sqrt(
                Math.pow(dropPoint.x - childCenter.x, 2) +
                Math.pow(dropPoint.y - childCenter.y, 2)
            );

            if (distance < closestDistance) {
                closestDistance = distance;
                closestElement = child;

                if (Math.abs(dropPoint.y - childCenter.y) < rect.height / 2) {
                    insertAfter = dropPoint.x > childCenter.x;
                } else {
                    insertAfter = dropPoint.y > childCenter.y;
                }
            }
        });

        return { closestElement, insertAfter };
    }

    insertElement(e) {
        const dropPoint = this.getDropPoint(e);
        const { closestElement, insertAfter } = this.findClosestElement(dropPoint);
        this.newOrder = closestElement.dataset.order;

        if (closestElement) {
            if (insertAfter) {
                this.newOrder++;
                this.playlist.dataset.order = this.newOrder;
                closestElement.after(this.playlist);
            } else {
                this.playlist.dataset.order = this.newOrder;
                closestElement.before(this.playlist);
            }
        }
    }
}

class CleanOrderHandler {
    constructor() {
        this.associatedPlaylists = document.getElementById('associated-playlists')
        this.playlistNonAssociees = document.getElementById('unassociated-playlists')
    }

    getAssociatedPlaylists() {
        return this.associatedPlaylists
    }

    reorderFrom(order = 0) {
        let listEl = this.associatedPlaylists.getElementsByClassName('playlist-dragAndDrop');
        for (let i = 1; i <= listEl.length; i++) {
            if (i + 1 >= order && order > 1) {
                listEl[i].dataset.order = parseInt(listEl[i].dataset.order) + 1
            }
        }
        return this
    }

    trueReorder() {
        let listEl = this.associatedPlaylists.getElementsByClassName('playlist-dragAndDrop');
        let order = 1;
        for (let i = 0; i < listEl.length; i++) {
            listEl[i].dataset.order = order;
            order++;
        }
        return this
    }

    resetBadge() {
        let listEl = this.associatedPlaylists.getElementsByClassName('playlist-dragAndDrop');
        for (let i = 0; i < listEl.length; i++) {
            this.removeBadge(listEl[i].id, false)
            this.addBadge(listEl[i].id, listEl[i].dataset.order)
        }
        this.cleanUnsassociatedBadge()
 
        return this
    }

    cleanUnsassociatedBadge(){
        let listUnassociated =  this.playlistNonAssociees.getElementsByClassName('playlist-dragAndDrop');
        for (let i = 0; i < listUnassociated.length; i++) {
            this.removeBadge(listUnassociated[i].id, true)
        }
        return this
    }

    removeBadge(playlistId, cleanData = false) {
        let playlistElement = document.getElementById(playlistId)
        if (cleanData) {
            playlistElement.dataset.order = ""
        }
        const badge = playlistElement.getElementsByClassName('badge-order')[0];
        if (badge == undefined) return
        badge.remove();
    }

    addBadge(playlistId, order = 0) {
        let playlistElement = document.getElementById(playlistId)
        const badge = document.createElement('span');
        badge.classList = "badge-order position-absolute top-0 start-100 translate-middle badge rounded-pill bg-primary";
        if (order <= 0) {
            badge.textContent = '+';
        } else {
            badge.textContent = order;
            playlistElement.dataset.order = order
        }
        playlistElement.appendChild(badge);
    }

}


function initOrderBadge() {
    cleanorder = new CleanOrderHandler()
    cleanorder.resetBadge()
}

function setEventDragAndDrop() {
    // Sélectionner les éléments HTML
    const playlistNonAssociees = document.getElementById('unassociated-playlists');
    const playlistAssociees = document.getElementById('associated-playlists');

    // Définir les événements de drag and drop
    playlistAssociees.addEventListener('dragstart', (e) => { // from associées
        e.dataTransfer.setData('id', e.target.id);
        e.dataTransfer.setData('dragstart', 'playlistAssociees');
    });

    playlistNonAssociees.addEventListener('dragstart', (e) => { // from non associées
        e.dataTransfer.setData('id', e.target.id);
        e.dataTransfer.setData('dragstart', 'playlistNonAssociees');
    });

    playlistAssociees.addEventListener('dragover', (e) => {
        e.preventDefault();
    });

    playlistNonAssociees.addEventListener('dragover', (e) => {
        e.preventDefault();
    });

    playlistAssociees.addEventListener('drop', (e) => { // to associées
        e.preventDefault();
        orderNewElement = null
        dragstart = e.dataTransfer.getData('dragstart');

        const children = [...playlistAssociees.children];
        const id = e.dataTransfer.getData('id');
        const playlist = document.getElementById(id);
        if (dragstart == 'playlistAssociees') {

            let handler = new DropPointHandler(playlist, children)
            playlist.remove();
            handler.insertElement(e)
            orderNewElement = handler.getNewOrder()
            updateMusic(playlist.id, orderNewElement);

        } else {
            if (children.length === 0) {
                playlistAssociees.appendChild(playlist);
            } else {
                let handler = new DropPointHandler(playlist, children)
                handler.insertElement(e)
                orderNewElement = handler.getNewOrder()
            }
            addMusic(playlist.id, orderNewElement);
        }
        checkEmptyPlaylist();

        cleanorder = new CleanOrderHandler()
        cleanorder.trueReorder().resetBadge()

    });

    playlistNonAssociees.addEventListener('drop', (e) => { // to non associées
        e.preventDefault();
        dragstart = e.dataTransfer.getData('dragstart');
        if (dragstart == 'playlistNonAssociees') {
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
function addMusic(idPlaylist, newOrder) {
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
            newOrder: newOrder
        })
    })
        .then(response => response.json())
        .then(data => {
            cleanorder = new CleanOrderHandler()
            cleanorder.reorderFrom(data.order).resetBadge()
        })
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
        .then(data => {
            cleanorder = new CleanOrderHandler()
            cleanorder.trueReorder().resetBadge()
        })
        .catch(error => console.error(error));
}

function updateMusic(idPlaylist, newOrder) {
    const associatedPlaylists = document.getElementById('associated-playlists');
    const url = associatedPlaylists.dataset.url;
    var csrfToken = getCookie('csrftoken');
    fetch(url, {
        method: 'UPDATE',
        headers: {
            'X-CSRFToken': csrfToken,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            idPlaylist: idPlaylist,
            newOrder: newOrder
        })
    })
        .then(response => response.json())
        .then(data => {
            cleanorder = new CleanOrderHandler()
            cleanorder.trueReorder().resetBadge()
        })
        .catch(error => console.error(error));
}



