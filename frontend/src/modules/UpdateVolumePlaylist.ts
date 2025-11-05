import Csrf from "@/modules/General/Csrf";
import { ButtonPlaylist } from "./ButtonPlaylist";
import { SearchMusicElement } from "@/modules/MusicElementSearcher";
import UpdateVolumeElement from "@/modules/UpdateVolumeElement";

import { method, uri } from '@/type/General';

class UpdateVolumePlaylist {
    buttonPlaylist: ButtonPlaylist
    volume: number

    constructor(buttonPlaylist: ButtonPlaylist, volume: number) {
        this.buttonPlaylist = buttonPlaylist;
        this.volume = volume
    }


    updateVolume() {
        this.buttonPlaylist.dataset.playlistVolume = this.volume.toString();
        const listMusic = SearchMusicElement.searchByButton(this.buttonPlaylist);

        for (const musicElement of listMusic) {
            musicElement.setDefaultVolume(this.buttonPlaylist.getVolume())
            const updateVolume = new UpdateVolumeElement(musicElement);
            updateVolume.clearCache(musicElement.idPlaylist).update()
        }

    }

    updateBackend(uri: uri) {
        const method = 'POST' as method;
        fetch(uri, {
            method: method,
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'X-CSRFToken': Csrf.getToken()!
            },
            body: JSON.stringify({
                volume: this.volume
            })
        });
    }

}

export { UpdateVolumePlaylist };