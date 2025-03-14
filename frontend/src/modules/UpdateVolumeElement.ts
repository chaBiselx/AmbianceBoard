import { MusicElement } from "@/modules/MusicElement";
import { MixerManager } from "@/modules/MixerManager";
import { ButtonPlaylistFinder } from "@/modules/ButtonPlaylist";

class UpdateVolumeElement {
    musicElement: MusicElement

    constructor(audioElement: MusicElement) {
        this.musicElement = audioElement;
    }

    update() {
        let VolumeDefault = this.getVolumeDefault();
        let VolumeFade = this.musicElement.levelFade
        let VolumeMixerGeneral = this.getVolumeMixerGeneral()
        let VolumeMixerType = this.getVolumeMixerType(this.musicElement.playlistType)
        let new_volume = Math.min(1, Math.max(0, VolumeDefault * VolumeFade * VolumeMixerGeneral * VolumeMixerType))
        // console.log(`VolumeDefault: ${VolumeDefault}, VolumeFade: ${VolumeFade}, VolumeMixerGeneral: ${VolumeMixerGeneral}, VolumeMixerType: ${VolumeMixerType}, new_volume: ${new_volume}`);
        this.musicElement.DOMElement.volume = new_volume;
    }

    getVolumeDefault(): number {
        let button = ButtonPlaylistFinder.search(this.musicElement.idPlaylist);
        if (button) {
            return button.getVolume();
        }

        return this.musicElement.defaultVolume;
    }

    getVolumeMixerGeneral(): number {
        return MixerManager.getMixerValue('general');
    }

    getVolumeMixerType(type: string): number {
        return MixerManager.getMixerValue(type);
    }
}

export default UpdateVolumeElement;