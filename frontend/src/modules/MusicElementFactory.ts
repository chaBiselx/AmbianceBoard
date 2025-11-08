import { MusicElement } from '@/modules/MusicElement';
import { ButtonPlaylist } from '@/modules/ButtonPlaylist';
import Boolean from "@/modules/Util/Boolean";
import Config from '@/modules/General/Config';
import SharedSoundBoardUtil from '@/modules/SharedSoundBoardUtil';

/**
 * DTO pour la configuration d'un MusicElement
 */
export interface MusicElementDTO {
    butonPlaylistToken: string | null;
    defaultVolume: number;
    fadeIn: boolean;
    fadeInType: string;
    fadeInDuration: number;
    fadeOut: boolean;
    fadeOutType: string;
    fadeOutDuration: number;
    playlistType: string;
    idPlaylist: string;
    playlistLoop: boolean;
    delay: number;
    baseUrl: string;
    durationRemainingTriggerNextMusic: number;
    fadeOffOnStop: boolean;
    fadeOffOnStopDuration: number;
    fadeOffOnStopType: string;
}

/**
 * Factory pour créer des instances de MusicElement
 */
export class MusicElementFactory {
    /**
     * Crée un MusicElement à partir d'un HTMLAudioElement existant
     */
    static fromAudioElement(element: HTMLAudioElement): MusicElement {
        const dto = this.extractDTOFromAudioElement(element);
        return this.createFromDTO(dto, element);
    }

    /**
     * Crée un MusicElement à partir d'un ButtonPlaylist
     */
    static fromButtonPlaylist(buttonPlaylist: ButtonPlaylist): MusicElement {
        const dto = this.extractDTOFromButtonPlaylist(buttonPlaylist);
        const audioElement = this.createAudioElement(buttonPlaylist, dto);
        return this.createFromDTO(dto, audioElement);
    }

    /**
     * Crée un MusicElement à partir d'un DTO et d'un élément audio
     */
    private static createFromDTO(dto: MusicElementDTO, audioElement: HTMLAudioElement): MusicElement {
        const musicElement = new MusicElement(audioElement, dto);
        return musicElement;
    }

    /**
     * Extrait le DTO à partir d'un HTMLAudioElement
     */
    private static extractDTOFromAudioElement(element: HTMLAudioElement): MusicElementDTO {
        return {
            butonPlaylistToken: element.dataset.butonPlaylistToken || null,
            defaultVolume: element.dataset.defaultvolume
                ? Number.parseFloat(element.dataset.defaultvolume)
                : 1,
            fadeIn: element.dataset.fadein === "true",
            fadeInType: element.dataset.fadeintype || 'linear',
            fadeInDuration: element.dataset.fadeinduration
                ? Number.parseFloat(element.dataset.fadeinduration)
                : 0,
            fadeOut: element.dataset.fadeout === "true",
            fadeOutType: element.dataset.fadeouttype || 'linear',
            fadeOutDuration: element.dataset.fadeoutduration
                ? Number.parseFloat(element.dataset.fadeoutduration)
                : 0,
            playlistType: element.dataset.playlisttype || '',
            idPlaylist: element.dataset.playlistid || '',
            playlistLoop: element.dataset.playlistloop === "true",
            delay: element.dataset.playlistdelay
                ? Number.parseFloat(element.dataset.playlistdelay)
                : 0,
            baseUrl: element.dataset.baseurl || '',
            durationRemainingTriggerNextMusic: element.dataset.durationremainingtriggernextmusic
                ? Number.parseFloat(element.dataset.durationremainingtriggernextmusic)
                : 0,
            fadeOffOnStop: element.dataset.fadeoffonstop === "true",
            fadeOffOnStopDuration: element.dataset.fadeoffonstopduration
                ? Number.parseFloat(element.dataset.fadeoffonstopduration)
                : 0,
            fadeOffOnStopType: element.dataset.fadeoffonstoptype || 'linear',
        };
    }

    /**
     * Extrait le DTO à partir d'un ButtonPlaylist
     */
    private static extractDTOFromButtonPlaylist(buttonPlaylist: ButtonPlaylist): MusicElementDTO {
        return {
            butonPlaylistToken: buttonPlaylist.getToken(),
            defaultVolume: buttonPlaylist.dataset.playlistVolume
                ? buttonPlaylist.getVolume()
                : 1,
            fadeIn: buttonPlaylist.dataset.playlistFadein
                ? Boolean.convert(buttonPlaylist.dataset.playlistFadein)
                : false,
            fadeInType: buttonPlaylist.dataset.playlistFadeintype || 'linear',
            fadeInDuration: buttonPlaylist.dataset.playlistFadeinduration
                ? Number.parseFloat(buttonPlaylist.dataset.playlistFadeinduration)
                : 0,
            fadeOut: buttonPlaylist.dataset.playlistFadeout
                ? Boolean.convert(buttonPlaylist.dataset.playlistFadeout)
                : false,
            fadeOutType: buttonPlaylist.dataset.playlistFadeouttype || 'linear',
            fadeOutDuration: buttonPlaylist.dataset.playlistFadeoutduration
                ? Number.parseFloat(buttonPlaylist.dataset.playlistFadeoutduration)
                : 0,
            playlistType: buttonPlaylist.dataset.playlistType || '',
            idPlaylist: buttonPlaylist.idPlaylist,
            playlistLoop: buttonPlaylist.dataset.playlistLoop
                ? Boolean.convert(buttonPlaylist.dataset.playlistLoop)
                : false,
            delay: buttonPlaylist.dataset.playlistDelay
                ? Number.parseFloat(buttonPlaylist.dataset.playlistDelay)
                : 0,
            baseUrl: buttonPlaylist.dataset.playlistUri || '',
            durationRemainingTriggerNextMusic: buttonPlaylist.dataset.playlistDurationremainingtriggernextmusic
                ? Number.parseFloat(buttonPlaylist.dataset.playlistDurationremainingtriggernextmusic)
                : 0,
            fadeOffOnStop: buttonPlaylist.dataset.playlistFadeoffonstop
                ? Boolean.convert(buttonPlaylist.dataset.playlistFadeoffonstop)
                : false,
            fadeOffOnStopDuration: buttonPlaylist.dataset.playlistFadeoffonstopduration
                ? Number.parseFloat(buttonPlaylist.dataset.playlistFadeoffonstopduration)
                : 0,
            fadeOffOnStopType: buttonPlaylist.dataset.playlistFadeoffonstoptype || 'linear',
        };
    }

    /**
     * Crée un élément audio HTML à partir d'un ButtonPlaylist
     */
    private static createAudioElement(buttonPlaylist: ButtonPlaylist, dto: MusicElementDTO): HTMLAudioElement {
        const audioElement = document.createElement('audio');
        audioElement.className = `playlist-audio-${buttonPlaylist.idPlaylist}`;
        audioElement.classList.add('audio-' + buttonPlaylist.dataset.playlistType);

        // Configurer la source
        let src = dto.baseUrl;
        if (!this.isSlave()) {
            src += "?i=" + Date.now();
        }
        audioElement.src = src;
        audioElement.controls = Config.DEBUG;

        // Définir les attributs data-*
        this.setDataAttributes(audioElement, dto);

        return audioElement;
    }

    /**
     * Définit les attributs data-* sur l'élément audio
     */
    private static setDataAttributes(audioElement: HTMLAudioElement, dto: MusicElementDTO): void {
        if (dto.butonPlaylistToken) {
            audioElement.dataset.butonPlaylistToken = dto.butonPlaylistToken;
        }
        audioElement.dataset.defaultvolume = dto.defaultVolume.toString();
        audioElement.dataset.fadein = dto.fadeIn.toString();
        audioElement.dataset.fadeintype = dto.fadeInType;
        audioElement.dataset.fadeinduration = dto.fadeInDuration.toString();
        audioElement.dataset.fadeout = dto.fadeOut.toString();
        audioElement.dataset.fadeouttype = dto.fadeOutType;
        audioElement.dataset.fadeoutduration = dto.fadeOutDuration.toString();
        audioElement.dataset.playlisttype = dto.playlistType;
        audioElement.dataset.playlistid = dto.idPlaylist;
        audioElement.dataset.playlistloop = dto.playlistLoop.toString();
        audioElement.dataset.playlistdelay = dto.delay.toString();
        audioElement.dataset.baseurl = dto.baseUrl;
        audioElement.dataset.durationremainingtriggernextmusic = dto.durationRemainingTriggerNextMusic.toString();
        audioElement.dataset.fadeoffonstop = dto.fadeOffOnStop.toString();
        audioElement.dataset.fadeoffonstopduration = dto.fadeOffOnStopDuration.toString();
        audioElement.dataset.fadeoffonstoptype = dto.fadeOffOnStopType;
    }

    /**
     * Vérifie si c'est une page slave
     */
    private static isSlave(): boolean {
        return SharedSoundBoardUtil.isSlavePage();
    }
}
