import {MusicElement} from "../modules/MusicElement";
import {MixerManager} from "../modules/MixerManager";

class UpdateVolumeElement {
    musicElement:MusicElement

    constructor(audioElement:MusicElement) {
        this.musicElement = audioElement;
    }

    update() {
        let VolumeDefault = this.musicElement.defaultVolume
        let VolumeFade = this.musicElement.levelFade
        let VolumeMixerGeneral = this.getVolumeMixerGeneral()
        let VolumeMixerType = this.getVolumeMixerType(this.musicElement.playlistType)
        let new_volume = Math.min(1, Math.max(0, VolumeDefault * VolumeFade * VolumeMixerGeneral * VolumeMixerType))
        // console.log(`VolumeDefault: ${VolumeDefault}, VolumeFade: ${VolumeFade}, VolumeMixerGeneral: ${VolumeMixerGeneral}, VolumeMixerType: ${VolumeMixerType}`);
        this.musicElement.DOMElement.volume = new_volume;
    }

    getVolumeMixerGeneral() : number {
        return MixerManager.getMixerValue('general');
    }

    getVolumeMixerType(type : string) : number {
        return MixerManager.getMixerValue(type);
    }
}

export default UpdateVolumeElement;