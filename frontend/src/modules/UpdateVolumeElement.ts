import { MusicElement } from "@/modules/MusicElement";
import { MixerManager } from "@/modules/MixerManager";
import { ButtonPlaylistFinder } from "@/modules/ButtonPlaylist";
import Cookie from "@/modules/General/Cookie";
import { SharedSoundboardIdFinder } from "@/modules/SharedSoundboardCustomVolume"

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
        let VolumeSharedCustom = this.getVolumeSharedCustomCookie(this.musicElement.idPlaylist)
        let new_volume = Math.min(1, Math.max(0, this.truncDecimal(VolumeDefault * VolumeFade * VolumeMixerGeneral * VolumeMixerType * VolumeSharedCustom)));
        // console.log(`VolumeDefault: ${VolumeDefault}, VolumeFade: ${VolumeFade}, VolumeMixerGeneral: ${VolumeMixerGeneral}, VolumeMixerType: ${VolumeMixerType}, new_volume: ${new_volume}, VolumeSharedCustom: ${VolumeSharedCustom}`); // NOSONAR
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

    private getVolumeSharedCustomCookie(playlistId: string): number {
        const soundboardId = SharedSoundboardIdFinder.findSoundBoardId('template-shared-volume');
        if (!soundboardId) return 1;
        const cookieValue = Cookie.get(`SharedPlaylistCustomVolume_${soundboardId}`);
        const jsonValue = cookieValue ? JSON.parse(cookieValue) : {};
        return jsonValue[playlistId] / 100 || 1;
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