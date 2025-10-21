import Config from '@/modules/General/Config';
import Notification from '@/modules/General/Notifications';
import ConsoleCustom from '@/modules/General/ConsoleCustom';
import ConsoleTraceServeur from '@/modules/General/ConsoleTraceServeur';
import SharedSoundBoardWebSocket from '@/modules/SharedSoundBoardWebSocket';
import SharedSoundBoardUtil from '@/modules/SharedSoundBoardUtil';

import { ButtonPlaylist, ButtonPlaylistFinder } from '@/modules/ButtonPlaylist';
import * as Model from '@/modules/FadeStartegy';
import AudioFadeManager from '@/modules/AudioFadeManager';
import { SoundBoardManager } from '@/modules/SoundBoardManager';
import Cookie from '@/modules/General/Cookie';
import Boolean from "@/modules/Util/Boolean";
import Time from "@/modules/Util/Time";
import ConsoleTesteur from '@/modules/General/ConsoleTesteur';



class MusicElement {
    DOMElement: HTMLAudioElement
    idPlaylist: string = '';
    playlistType: string = '';
    defaultVolume: number = 1;
    levelFade: number = 1;
    fadeInOnGoing: boolean = false;
    fadeIn: boolean = false;
    fadeInType: string = 'linear';
    fadeInDuration: number = 0;
    fadeOut: boolean = false;
    fadeOutType: string = 'linear';
    playlistLoop: boolean = false;
    fadeOutDuration: number = 0;
    delay: number = 0;
    butonPlaylistToken: string | null = null;
    fadeInGoing: boolean = false;
    baseUrl: string = ''; // url of playlist to stream music
    WebSocketActive: boolean = false; // user has websocket connection to command shared soundboard


    constructor(Element: HTMLAudioElement | ButtonPlaylist) {
        if (Element instanceof HTMLAudioElement) {
            this.DOMElement = Element;
            this.setDefaultValue();
        } else {
            this.DOMElement = document.createElement('audio');
            this.setDefaultFromPlaylist(Element);
        }

        if (Cookie.get('WebSocketToken') != null) {
            this.WebSocketActive = true;
        }
    }

    private setDefaultValue() {
        if (this.DOMElement.dataset.butonPlaylistToken) {
            this.butonPlaylistToken = this.DOMElement.dataset.butonPlaylistToken;
        }
        if (this.DOMElement.dataset.defaultvolume) {
            this.defaultVolume = Number.parseFloat(this.DOMElement.dataset.defaultvolume);
        }
        if (this.DOMElement.dataset.fadein) {
            this.fadeIn = this.DOMElement.dataset.fadein == "true";
        }
        if (this.DOMElement.dataset.fadeintype) {
            this.fadeInType = this.DOMElement.dataset.fadeintype;
        }
        if (this.DOMElement.dataset.fadeinduration) {
            this.fadeInDuration = Number.parseFloat(this.DOMElement.dataset.fadeinduration);
        }
        if (this.DOMElement.dataset.fadeout) {
            this.fadeOut = this.DOMElement.dataset.fadeout == "true";
        }
        if (this.DOMElement.dataset.fadeouttype) {
            this.fadeOutType = this.DOMElement.dataset.fadeouttype;
        }
        if (this.DOMElement.dataset.fadeoutduration) {
            this.fadeOutDuration = Number.parseFloat(this.DOMElement.dataset.fadeoutduration);
        }
        if (this.DOMElement.dataset.playlisttype) {
            this.playlistType = this.DOMElement.dataset.playlisttype;
        }
        if (this.DOMElement.dataset.playlistid) {
            this.idPlaylist = this.DOMElement.dataset.playlistid;
        }
        if (this.DOMElement.dataset.playlistloop) {
            this.playlistLoop = this.DOMElement.dataset.playlistloop == "true";
        }
        if (this.DOMElement.dataset.playlistdelay) {
            this.delay = Number.parseFloat(this.DOMElement.dataset.playlistdelay);
        }
        if (this.DOMElement.dataset.baseurl) {
            this.baseUrl = this.DOMElement.dataset.baseurl!;
        }
    }

    private setDefaultFromPlaylist(buttonPlaylist: ButtonPlaylist): void {
        this.setDefaultVolumeFromPlaylist(buttonPlaylist);
        this.setFadeInFromPlaylist(buttonPlaylist);
        this.setFadeOutFromPlaylist(buttonPlaylist);
        this.setPlaylistTypeFromPlaylist(buttonPlaylist);
        this.setPlaylistIdFromPlaylist(buttonPlaylist);
        this.setPlaylistLoopFromPlaylist(buttonPlaylist);
        this.setPlaylistDelayFromPlaylist(buttonPlaylist);
        this.setButtonPlaylistTokenFromPlaylist(buttonPlaylist);
        this.setBaseURlFromPlaylist(buttonPlaylist);


        this.DOMElement.className = `playlist-audio-${buttonPlaylist.idPlaylist}`;

        this.DOMElement.classList.add('audio-' + buttonPlaylist.dataset.playlistType)
        let src = this.baseUrl
        if (!this.isSlave()) {
            src += "?i=" + Date.now();
        }
        this.DOMElement.src = src;
        this.DOMElement.controls = Config.DEBUG;
    }

    public setDefaultVolume(volume: number) {
        this.defaultVolume = volume;
        this.DOMElement.dataset.defaultvolume = this.defaultVolume.toString();
    }

    public addToDOM(): this {
        const audioElementDiv = document.getElementById(Config.SOUNDBOARD_DIV_ID_PLAYERS) as HTMLElement;
        audioElementDiv.appendChild(this.DOMElement);
        this.DOMElement.preload = 'metadata';


        return this
    }

    public delete() {
        ConsoleTesteur.log(`🗑️ [${this.idPlaylist}] delete() called - removing element and stopping API`);
        const buttonPlaylist = ButtonPlaylistFinder.search(this.idPlaylist) as ButtonPlaylist;
        buttonPlaylist.disactive();
        this.DOMElement.remove();

        this.callAPIToStop()
    }



    public setSpecificMusic(baseUrl: string) {
        this.baseUrl = baseUrl;
        this.DOMElement.dataset.baseurl = this.baseUrl;
        this.DOMElement.src = this.baseUrl;
    }

    public play() {

        ConsoleTesteur.log('play_action');
        ConsoleTesteur.log(`🎵 Play setup - ID: ${this.idPlaylist}, Token: ${this.butonPlaylistToken}, FadeIn: ${this.fadeIn}, FadeOut: ${this.fadeOut}`);
        
        // Log des listeners pour détecter les accumulations
        this.DOMElement.addEventListener('loadstart', () => {
            ConsoleTesteur.log(`🔄 [${this.idPlaylist}] Loading started - src: ${this.DOMElement.src}`);
        });
        
        this.DOMElement.addEventListener('loadeddata', () => {
            ConsoleTesteur.log(`📦 [${this.idPlaylist}] Data loaded - duration: ${this.DOMElement.duration}s, readyState: ${this.DOMElement.readyState}`);
        });
        
        this.DOMElement.addEventListener('canplay', () => {
            ConsoleTesteur.log(`✅ [${this.idPlaylist}] Can play - currentTime: ${this.DOMElement.currentTime}s`);
        });
        
        this.DOMElement.addEventListener('playing', () => {
            ConsoleTesteur.log(`▶️ [${this.idPlaylist}] Actually playing - currentTime: ${this.DOMElement.currentTime}s`);
        });
        
        this.DOMElement.addEventListener('error', this.handleAudioError);

        if (this.fadeIn) {
            this.addFadeIn();
        }

        if (this.hasFadeout()) {
            ConsoleTesteur.log(`🎚️ [${this.idPlaylist}] Setting up fadeout listeners - duration: ${this.fadeOutDuration}s`);
            this.DOMElement.addEventListener('ended', this.eventDeleteFadeOut);
            this.DOMElement.addEventListener('loadedmetadata', () => {
                ConsoleTesteur.log(`📊 [${this.idPlaylist}] Metadata loaded, adding timeupdate listener`);
                this.DOMElement.addEventListener('timeupdate', this.eventFadeOut);
            });

        } else {
            ConsoleTesteur.log(`🎚️ [${this.idPlaylist}] No fadeout, setting up simple end listener`);
            this.DOMElement.addEventListener('ended', this.eventDeleteNoFadeOut);
        }
        ConsoleTesteur.log(`▶️ Play ${this.idPlaylist} ${this.isSlave()}`);

        this.DOMElement.play().then(() => {
            ConsoleTesteur.log(`✨ [${this.idPlaylist}] Play promise resolved`);
        }).catch((error) => {
            ConsoleTesteur.log(`❌ [${this.idPlaylist}] Play promise rejected: ${error}`);
        });
    }

    public checkLoop(): boolean {
        return this.playlistLoop && !this.isSlave()
    }

    public addFadeIn() {
        this.levelFade = 0;

        this.fadeInGoing = true;

        let typeFade = Model.default.FadeSelector.selectTypeFade(this.fadeInType)

        let audioFade = new AudioFadeManager(this, typeFade, true, () => {
            this.levelFade = 1;
            this.fadeInGoing = false;
        });
        audioFade.setDuration(this.fadeInDuration);
        this.DOMElement.addEventListener('playing', () => {
            let time = Date.now();
            while (this.DOMElement.readyState != 2) {
                if (time + 1 < Date.now()) {
                    break;
                }
            }
            audioFade.start();
        })

    }

    public addFadeOut() {
        ConsoleCustom.log('addFadeOut');
        ConsoleTesteur.log(`🔉 [${this.idPlaylist}] addFadeOut called - fadeInGoing: ${this.fadeInGoing}, currentVolume: ${this.DOMElement.volume}`);
        if (this.fadeInGoing) {
            ConsoleCustom.log('ignore fade out if fade in not finished');
            ConsoleTesteur.log(`⚠️ [${this.idPlaylist}] FadeOut ignored - FadeIn still in progress`);
            return // ignore fade out if fade in not finished
        }

        let typeFade = Model.default.FadeSelector.selectTypeFade(this.fadeInType)
        ConsoleTesteur.log(`🎚️ [${this.idPlaylist}] Starting fadeout - type: ${this.fadeInType}, duration: ${this.fadeOutDuration}s`);
        let audioFade = new AudioFadeManager(this, typeFade, false, () => {
            this.levelFade = 1;
            ConsoleTesteur.log(`✅ [${this.idPlaylist}] FadeOut completed`);
        });
        audioFade.setDuration(this.fadeOutDuration);
        audioFade.start();
    }

    private isSlave(): boolean {
        return SharedSoundBoardUtil.isSlavePage()
    }

    private eventFadeOut(event: Event) {
        ConsoleCustom.log('eventFadeOut');
        let new_music = new MusicElement(event.target as HTMLAudioElement);
        const timeRemaining = this.timeRemaining();
        ConsoleTesteur.log(`⏱️ [${new_music.idPlaylist}] TimeUpdate - Current: ${new_music.DOMElement.currentTime.toFixed(2)}s, Remaining: ${timeRemaining.toFixed(2)}s, FadeOutDuration: ${new_music.fadeOutDuration}s`);
        
        if (timeRemaining <= new_music.fadeOutDuration && new_music.hasFadeout()) {
            ConsoleTesteur.log(`🎚️ [${new_music.idPlaylist}] Fadeout triggered! Removing timeupdate listener`);
            const buttonPlaylist = ButtonPlaylistFinder.search(new_music.idPlaylist);
            if (buttonPlaylist) {
                new_music.DOMElement.removeEventListener('timeupdate', new_music.eventFadeOut);
                ConsoleTesteur.log(`🔇 [${new_music.idPlaylist}] Starting fadeout, Token: ${new_music.butonPlaylistToken}, ButtonToken: ${buttonPlaylist.getToken()}`);
                new_music.addFadeOut();
                if (new_music.checkLoop()) {
                    ConsoleTesteur.log(`🔁 [${new_music.idPlaylist}] Loop enabled, scheduling next play`);
                    new_music.applyDelay(() => {
                        ConsoleTesteur.log(`🔄 [${new_music.idPlaylist}] Delay finished, creating new playlist link`);
                        SoundBoardManager.createPlaylistLink(buttonPlaylist);
                    })
                } else {
                    ConsoleTesteur.log(`⏹️ [${new_music.idPlaylist}] No loop, disabling button`);
                    buttonPlaylist.disactive();
                }
            } else {
                ConsoleTesteur.log(`⚠️ [${new_music.idPlaylist}] ButtonPlaylist not found!`);
            }
        }
    }

    /**
     * Check if the audio element has fade out.
     * 
     * @returns True if the audio element has fade out, false otherwise.
     */
    private hasFadeout(): boolean {
        return this.fadeOut;
    }

    /**
     * Get the remaining time of the audio element.
     * @returns The remaining time in seconds.
     */
    private timeRemaining(): number {
        return this.DOMElement.duration - this.DOMElement.currentTime;
    }

    private getTimeDelay() {
        if (this.delay > 0) {
            return Math.floor(Math.random() * this.delay * 100) / 100;
        }
        return 0;
    }

    private applyDelay(callback: () => void) {
        ConsoleTesteur.log(`applyDelay => ${this.delay} ${typeof this.delay}`);
        if (this.delay > 0) {
            const delay = this.getTimeDelay();
            ConsoleTesteur.log("delay: " + delay);
            setTimeout(() => {
                ConsoleTesteur .log("applyDelay callback: ");
                const buttonPlaylist = ButtonPlaylistFinder.search(this.idPlaylist);
                if (buttonPlaylist && buttonPlaylist.isActive() && this.butonPlaylistToken == buttonPlaylist.getToken()) {
                    callback()
                }
            }, Time.get_seconds(delay));
        } else {
            callback();
        }
    }

    private eventDeleteFadeOut(event: Event) {
        ConsoleCustom.log('eventDeleteFadeOut');
        let new_music = new MusicElement(event.target as HTMLAudioElement);
        ConsoleTesteur.log(`🗑️ [${new_music.idPlaylist}] eventDeleteFadeOut - Removing audio element, currentTime: ${new_music.DOMElement.currentTime.toFixed(2)}s, duration: ${new_music.DOMElement.duration.toFixed(2)}s`);
        new_music.DOMElement.remove();
    }

    private eventDeleteNoFadeOut(event: Event) {
        ConsoleCustom.log('eventDeleteNoFadeOut');
        let new_music = new MusicElement(event.target as HTMLAudioElement);
        ConsoleTesteur.log(`🗑️ [${new_music.idPlaylist}] eventDeleteNoFadeOut - currentTime: ${new_music.DOMElement.currentTime.toFixed(2)}s, duration: ${new_music.DOMElement.duration.toFixed(2)}s`);
        new_music.DOMElement.remove();
        if (new_music.checkLoop()) {
            const buttonPlaylist = ButtonPlaylistFinder.search(new_music.idPlaylist) as ButtonPlaylist;
            ConsoleTesteur.log(`🔁 [${new_music.idPlaylist}] Loop enabled (no fadeout), scheduling next play`);
            new_music.applyDelay(() => {
                ConsoleTesteur.log(`🔄 [${new_music.idPlaylist}] Delay finished, creating new playlist link`);
                SoundBoardManager.createPlaylistLink(buttonPlaylist);
            })
        } else {
            const buttonPlaylist = ButtonPlaylistFinder.search(new_music.idPlaylist) as ButtonPlaylist;
            ConsoleTesteur.log(`⏹️ [${new_music.idPlaylist}] No loop, disabling button`);
            buttonPlaylist.disactive();
        }
    }

    private callAPIToStop() {
        ConsoleTesteur.log(`enter MusicElement.callAPIToStop ${this.WebSocketActive} ${this.isSlave()}`);
        if (this.WebSocketActive && !this.isSlave()) {
            ConsoleTesteur.log("WebSocket Master call from MusicElement.callAPIToStop");

            (SharedSoundBoardWebSocket.getMasterInstance()).sendMessage({
                "type": "music_stop",
                "track": null,
                "playlist_uuid": this.idPlaylist,
            });
        }
    }

    private setDefaultVolumeFromPlaylist(buttonPlaylist: ButtonPlaylist): void {
        if (buttonPlaylist.dataset.playlistVolume) {
            this.setDefaultVolume(buttonPlaylist.getVolume());
        }
    }

    private setFadeInFromPlaylist(buttonPlaylist: ButtonPlaylist): void {
        if (buttonPlaylist.dataset.playlistFadein) {
            this.fadeIn = Boolean.convert(buttonPlaylist.dataset.playlistFadein);
            this.DOMElement.dataset.fadein = this.fadeIn.toString();
        }
        if (buttonPlaylist.dataset.playlistFadeintype) {
            this.fadeInType = buttonPlaylist.dataset.playlistFadeintype;
            this.DOMElement.dataset.fadeintype = this.fadeInType;
        }
        if (buttonPlaylist.dataset.playlistFadeinduration) {
            this.fadeInDuration = Number.parseFloat(buttonPlaylist.dataset.playlistFadeinduration);
            this.DOMElement.dataset.fadeinduration = this.fadeInDuration.toString();
        }
    }

    private setFadeOutFromPlaylist(buttonPlaylist: ButtonPlaylist): void {
        if (buttonPlaylist.dataset.playlistFadeout) {
            this.fadeOut = Boolean.convert(buttonPlaylist.dataset.playlistFadeout);
            this.DOMElement.dataset.fadeout = this.fadeOut.toString();
        }
        if (buttonPlaylist.dataset.playlistFadeouttype) {
            this.fadeOutType = buttonPlaylist.dataset.playlistFadeouttype;
            this.DOMElement.dataset.fadeouttype = this.fadeOutType;
        }
        if (buttonPlaylist.dataset.playlistFadeoutduration) {
            this.fadeOutDuration = Number.parseFloat(buttonPlaylist.dataset.playlistFadeoutduration);
            this.DOMElement.dataset.fadeoutduration = this.fadeOutDuration.toString();
        }
    }

    private setPlaylistTypeFromPlaylist(buttonPlaylist: ButtonPlaylist): void {
        if (buttonPlaylist.dataset.playlistType) {
            this.playlistType = buttonPlaylist.dataset.playlistType;
            this.DOMElement.dataset.playlisttype = this.playlistType;
        }
    }

    private setPlaylistIdFromPlaylist(buttonPlaylist: ButtonPlaylist): void {
        if (buttonPlaylist.idPlaylist) {
            this.idPlaylist = buttonPlaylist.idPlaylist;
            this.DOMElement.dataset.playlistid = this.idPlaylist;
        }
    }

    private setPlaylistLoopFromPlaylist(buttonPlaylist: ButtonPlaylist): void {
        if (buttonPlaylist.dataset.playlistLoop) {
            this.playlistLoop = Boolean.convert(buttonPlaylist.dataset.playlistLoop);
            this.DOMElement.dataset.playlistloop = this.playlistLoop.toString();
        }
    }

    private setPlaylistDelayFromPlaylist(buttonPlaylist: ButtonPlaylist): void {
        if (buttonPlaylist.dataset.playlistDelay) {
            this.delay = Number.parseFloat(buttonPlaylist.dataset.playlistDelay);
            this.DOMElement.dataset.playlistdelay = this.delay.toString();
        }
    }

    private setButtonPlaylistTokenFromPlaylist(buttonPlaylist: ButtonPlaylist): void {
        const token = buttonPlaylist.getToken();
        if (token) {
            this.butonPlaylistToken = token;
            this.DOMElement.dataset.butonPlaylistToken = this.butonPlaylistToken;
        }
    }

    private setBaseURlFromPlaylist(buttonPlaylist: ButtonPlaylist): void {
        this.baseUrl = buttonPlaylist.dataset.playlistUri!;
        this.DOMElement.dataset.baseurl = this.baseUrl;
    }



    private handleAudioError(event: Event) {
        if (event.target && event.target instanceof HTMLAudioElement) {
            const audioElement = event.target;
            let new_music = new MusicElement(audioElement);
            ConsoleTesteur.log(`❌ [${new_music.idPlaylist}] Audio Error - code: ${audioElement.error?.code}, message: ${audioElement.error?.message}, src: ${audioElement.src}`);
            
            if (audioElement.error && audioElement.error.code === 4) { // => ERROR 404
                // Log toutes les informations disponibles

                ConsoleTraceServeur.error('handleAudioError', audioElement.error.code, audioElement.error.message, new_music.idPlaylist, new_music.baseUrl, audioElement.src);

                const buttonPlaylist = ButtonPlaylistFinder.search(new_music.idPlaylist) as ButtonPlaylist;
                buttonPlaylist.disactive();
                Notification.createClientNotification({ message: 'Aucune musique n\'est presente dans cette playlist', type: 'danger', duration: 2000 });
                event.target.remove();
            }
        }
    }

}

class SearchMusicElement {
    static searchByButton(buttonPlaylist: ButtonPlaylist): MusicElement[] {
        const audio = document.getElementsByClassName('playlist-audio-' + buttonPlaylist.idPlaylist) as HTMLCollectionOf<HTMLAudioElement>;
        const listMusic: MusicElement[] = [];
        if (audio.length > 0) {
            for (let audioDom of audio) {
                listMusic.push(new MusicElement(audioDom));
            }
        }
        return listMusic;
    }
}

class ListingAudioElement {
    static getListingAudioElement(type: string): MusicElement[] {
        const audioElementDiv = document.getElementById(Config.SOUNDBOARD_DIV_ID_PLAYERS) as HTMLElement;
        const audio = audioElementDiv.getElementsByClassName('audio-' + type) as HTMLCollectionOf<HTMLAudioElement>;
        const listingMusicElement: MusicElement[] = []
        for (let audioDom of audio) {
            listingMusicElement.push(new MusicElement(audioDom));
        };
        return listingMusicElement;
    }

    static getListAllAudio(): MusicElement[] {
        const audioElementDiv = document.getElementById(Config.SOUNDBOARD_DIV_ID_PLAYERS) as HTMLElement;
        const audio = audioElementDiv.getElementsByTagName('audio');
        const listingMusicElement: MusicElement[] = []
        for (let audioDom of audio) {
            listingMusicElement.push(new MusicElement(audioDom));
        };
        return listingMusicElement;
    }
}

export { MusicElement, ListingAudioElement, SearchMusicElement };

