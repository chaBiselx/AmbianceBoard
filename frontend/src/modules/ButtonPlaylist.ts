
const TRUE = 'True';//TODO fix type soundboard_read

class ButtonPlaylist {
    buttonElement: HTMLElement;
    idPlaylist: string;
    dataset: DOMStringMap;
    singleConcurrentread: boolean
    playlistType: string

    constructor(el: HTMLElement) {
        this.buttonElement = el;
        this.idPlaylist = el.dataset.playlistId!;
        this.singleConcurrentread = (el.dataset.playlistSingleconcurrentread == TRUE) ? true : false;
        this.playlistType = el.dataset.playlistType!;
        this.dataset = el.dataset;
    }

    delete() {
        this.buttonElement.remove();
    }

    disactive() {
        this.buttonElement.classList.remove("active-playlist")
    }

    active() {
        this.buttonElement.classList.add("active-playlist")
    }

}

class ButtonPlaylistFinder {
    static search(idPlaylist: string): ButtonPlaylist | null {
        const buttonElement = document.getElementById(`playlist-${idPlaylist}`) as HTMLElement;
        if (buttonElement) {
            return new ButtonPlaylist(buttonElement);
        }
        return null;
    }
}

class ListingButtonPlaylist {
    static getListingAudioElement(playlistType: string): ButtonPlaylist[] {
        const buttonPlaylists = document.getElementsByClassName(`playlist-${playlistType}`) as HTMLCollectionOf<HTMLElement>;
        const buttonPlaylistList: ButtonPlaylist[] = [];
        for (let i = 0; i < buttonPlaylists.length; i++) {
            buttonPlaylistList.push(new ButtonPlaylist(buttonPlaylists[i]));
        }
        return buttonPlaylistList;
    }
}



export { ButtonPlaylist, ButtonPlaylistFinder, ListingButtonPlaylist };