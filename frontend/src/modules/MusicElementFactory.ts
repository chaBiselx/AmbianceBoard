import { MusicElement } from '@/modules/MusicElement';
import { ButtonPlaylist } from '@/modules/ButtonPlaylist';
import Boolean from "@/modules/Util/Boolean";
import Config from '@/modules/General/Config';
import SharedSoundBoardUtil from '@/modules/SharedSoundBoardUtil';
import HtmlAudioAdapter from '@/modules/Audio/HtmlAudioAdapter';
import { IAudioAdapter } from '@/modules/Audio/IAudioAdapter';
import WebAudioAdapter from '@/modules/Audio/WebAudioAdapter';

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
        const adapter = this.createAdapter(element);
        const dto = this.extractDTOFromAudioAdapter(adapter);
        return this.createFromDTO(dto, adapter);
    }

    /**
     * Crée un MusicElement à partir d'un ButtonPlaylist
     */
    static fromButtonPlaylist(buttonPlaylist: ButtonPlaylist): MusicElement {
        const dto = this.extractDTOFromButtonPlaylist(buttonPlaylist);
        const audioAdapter = this.createAudioAdapter(buttonPlaylist, dto);
        return this.createFromDTO(dto, audioAdapter);
    }

    /**
     * Crée un MusicElement à partir d'un DTO et d'un élément audio
     */
    private static createFromDTO(dto: MusicElementDTO, audioAdapter: IAudioAdapter): MusicElement {
        const musicElement = new MusicElement(audioAdapter, dto);
        return musicElement;
    }

    /**
     * Extrait le DTO à partir d'un HTMLAudioElement
     */
    private static extractDTOFromAudioAdapter(adapter: IAudioAdapter): MusicElementDTO {
        return {
            butonPlaylistToken: adapter.getDatasetValue('butonPlaylistToken') || null,
            defaultVolume: adapter.getDatasetValue('defaultvolume')
                ? Number.parseFloat(adapter.getDatasetValue('defaultvolume')!)
                : 1,
            fadeIn: adapter.getDatasetValue('fadein') === "true",
            fadeInType: adapter.getDatasetValue('fadeintype') || 'linear',
            fadeInDuration: adapter.getDatasetValue('fadeinduration')
                ? Number.parseFloat(adapter.getDatasetValue('fadeinduration')!)
                : 0,
            fadeOut: adapter.getDatasetValue('fadeout') === "true",
            fadeOutType: adapter.getDatasetValue('fadeouttype') || 'linear',
            fadeOutDuration: adapter.getDatasetValue('fadeoutduration')
                ? Number.parseFloat(adapter.getDatasetValue('fadeoutduration')!)
                : 0,
            playlistType: adapter.getDatasetValue('playlisttype') || '',
            idPlaylist: adapter.getDatasetValue('playlistid') || '',
            playlistLoop: adapter.getDatasetValue('playlistloop') === "true",
            delay: adapter.getDatasetValue('playlistdelay')
                ? Number.parseFloat(adapter.getDatasetValue('playlistdelay')!)
                : 0,
            baseUrl: adapter.getDatasetValue('baseurl') || '',
            durationRemainingTriggerNextMusic: adapter.getDatasetValue('durationremainingtriggernextmusic')
                ? Number.parseFloat(adapter.getDatasetValue('durationremainingtriggernextmusic')!)
                : 0,
            fadeOffOnStop: adapter.getDatasetValue('fadeoffonstop') === "true",
            fadeOffOnStopDuration: adapter.getDatasetValue('fadeoffonstopduration')
                ? Number.parseFloat(adapter.getDatasetValue('fadeoffonstopduration')!)
                : 0,
            fadeOffOnStopType: adapter.getDatasetValue('fadeoffonstoptype') || 'linear',
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
    private static createAudioAdapter(buttonPlaylist: ButtonPlaylist, dto: MusicElementDTO): IAudioAdapter {
        const audioElement = new Audio();
        console.log('================ ')
        console.log('audioElement ', typeof audioElement, buttonPlaylist.idPlaylist)
        console.log('================ ')
        const audioAdapter = this.createAdapter(audioElement);
        audioAdapter.setClassName(`playlist-audio-${buttonPlaylist.idPlaylist}`);
        audioAdapter.addClass('audio-' + buttonPlaylist.dataset.playlistType);

        // Configurer la source
        let src = dto.baseUrl;
        if (!this.isSlave()) {
            src += "?i=" + Date.now();
        }
        audioAdapter.setSource(src);
        audioAdapter.setControls(Config.DEBUG);

        // Définir les attributs data-*
        this.setDataAttributes(audioAdapter, dto);

        return audioAdapter;
    }

    private static createAdapter(audioElement: HTMLAudioElement): IAudioAdapter {
        if (WebAudioAdapter.isSupported()) {
            return new WebAudioAdapter(audioElement);
        }

        return new HtmlAudioAdapter(audioElement);
    }

    /**
     * Définit les attributs data-* sur l'élément audio
     */
    private static setDataAttributes(audioAdapter: IAudioAdapter, dto: MusicElementDTO): void {
        if (dto.butonPlaylistToken) {
            audioAdapter.setDatasetValue('butonPlaylistToken', dto.butonPlaylistToken);
        }
        audioAdapter.setDatasetValue('defaultvolume', dto.defaultVolume.toString());
        audioAdapter.setDatasetValue('fadein', dto.fadeIn.toString());
        audioAdapter.setDatasetValue('fadeintype', dto.fadeInType);
        audioAdapter.setDatasetValue('fadeinduration', dto.fadeInDuration.toString());
        audioAdapter.setDatasetValue('fadeout', dto.fadeOut.toString());
        audioAdapter.setDatasetValue('fadeouttype', dto.fadeOutType);
        audioAdapter.setDatasetValue('fadeoutduration', dto.fadeOutDuration.toString());
        audioAdapter.setDatasetValue('playlisttype', dto.playlistType);
        audioAdapter.setDatasetValue('playlistid', dto.idPlaylist);
        audioAdapter.setDatasetValue('playlistloop', dto.playlistLoop.toString());
        audioAdapter.setDatasetValue('playlistdelay', dto.delay.toString());
        audioAdapter.setDatasetValue('baseurl', dto.baseUrl);
        audioAdapter.setDatasetValue('durationremainingtriggernextmusic', dto.durationRemainingTriggerNextMusic.toString());
        audioAdapter.setDatasetValue('fadeoffonstop', dto.fadeOffOnStop.toString());
        audioAdapter.setDatasetValue('fadeoffonstopduration', dto.fadeOffOnStopDuration.toString());
        audioAdapter.setDatasetValue('fadeoffonstoptype', dto.fadeOffOnStopType);
    }

    /**
     * Vérifie si c'est une page slave
     */
    private static isSlave(): boolean {
        return SharedSoundBoardUtil.isSlavePage();
    }
}
