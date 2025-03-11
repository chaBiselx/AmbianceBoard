class OrganizerButtonPlaylist {
    playlist: HTMLDivElement;
    constructor(playlistId: string) {
        this.playlist = document.getElementById(playlistId) as HTMLDivElement;
    }    

    public removeBadge(cleanData = false) {
        if (cleanData) {
            this.playlist.dataset.order = ""
        }
        const badge = this.playlist.getElementsByClassName('badge-order')[0];
        if (badge == undefined) return
        badge.remove();
    }

    public addBadge(order = 0) {
        const badge = document.createElement('span');
        badge.classList = "badge-order position-absolute top-0 start-100 translate-middle badge rounded-pill bg-primary";
        if (order <= 0) {
            badge.textContent = '+';
        } else {
            badge.textContent = order.toString();
            this.playlist.dataset.order = order.toString();
        }
        this.playlist.appendChild(badge);
    }
}

export {OrganizerButtonPlaylist};