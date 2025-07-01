import { MusicElement } from "@/modules/MusicElement";
import { MixerManager } from "@/modules/MixerManager";
import { ButtonPlaylistFinder } from "@/modules/ButtonPlaylist";

class UpdateVolumeElement {
    musicElement: MusicElement
    private static mixerCache: Record<string, number> = {};

    constructor(audioElement: MusicElement) {
        this.musicElement = audioElement;
    }

    update() {
        let VolumeDefault = this.getVolumeDefault();
        let VolumeFade = this.musicElement.levelFade
        let VolumeMixerGeneral = this.getVolumeMixerValue('general')
        let VolumeMixerType = this.getVolumeMixerValue(this.musicElement.playlistType)
        let new_volume = Math.min(1, Math.max(0, this.truncDecimal(VolumeDefault * VolumeFade * VolumeMixerGeneral * VolumeMixerType)));
        // console.log(`VolumeDefault: ${VolumeDefault}, VolumeFade: ${VolumeFade}, VolumeMixerGeneral: ${VolumeMixerGeneral}, VolumeMixerType: ${VolumeMixerType}, new_volume: ${new_volume}`); // NOSONAR
        this.musicElement.DOMElement.volume = new_volume;
    }



    private getVolumeDefault(): number {
        const key = this.musicElement.idPlaylist
        if (!(key in UpdateVolumeElement.mixerCache)) {
            if (this.musicElement.defaultVolume) {
                UpdateVolumeElement.mixerCache[key] = this.musicElement.defaultVolume;
            } else {
                let button = ButtonPlaylistFinder.search(this.musicElement.idPlaylist);
                if (button) {
                    UpdateVolumeElement.mixerCache[key] = button.getVolume();
                }
            }

        }
        return UpdateVolumeElement.mixerCache[key];
    }

    private getVolumeMixerValue(type: string): number {
        if (!(type in UpdateVolumeElement.mixerCache)) {
            UpdateVolumeElement.mixerCache[type] = this.truncDecimal(MixerManager.getMixerValue(type));
        }
        return UpdateVolumeElement.mixerCache[type];
    }

    private truncDecimal(value: number): number {
        return Math.round(value * 100) / 100;
    }

    public clearCache( key: string) : this {
        delete UpdateVolumeElement.mixerCache[key];
        delete UpdateVolumeElement.mixerCache['general'];
        return this;
    }
}

export default UpdateVolumeElement;