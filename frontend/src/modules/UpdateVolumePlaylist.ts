import Csrf from "@/modules/General/Csrf";
import { ButtonPlaylist } from "./ButtonPlaylist";
import { SearchMusicElement } from "@/modules/MusicElementSearcher";
import UpdateVolumeElement from "@/modules/UpdateVolumeElement";

import { method, uri } from '@/type/General';

class UpdateVolumePlaylist {
    buttonPlaylist: ButtonPlaylist

    constructor(buttonPlaylist: ButtonPlaylist) {
        this.buttonPlaylist = buttonPlaylist;
    }

    public updateVolume(volume: number) {
        this.buttonPlaylist.dataset.playlistVolume = volume.toString();
        const listMusic = SearchMusicElement.searchByButton(this.buttonPlaylist);

        for (const musicElement of listMusic) {
            musicElement.setDefaultVolume(this.buttonPlaylist.getVolume())
            const updateVolume = new UpdateVolumeElement(musicElement);
            updateVolume.clearCache(musicElement.idPlaylist).update()
        }

    }

    public clearCache(){
        UpdateVolumeElement.clearAllCache();
    }

    public updateBackend(uri: uri, volume: number) {
        const method = 'POST' as method;
        fetch(uri, {
            method: method,
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'X-CSRFToken': Csrf.getToken()!
            },
            body: JSON.stringify({
                volume: volume
            })
        });
    }

}

export { UpdateVolumePlaylist };