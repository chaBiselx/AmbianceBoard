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
    duration: number | null = null;
    private boundEventFadeOut: (() => void) | null = null;


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

    /**
     * Récupère la durée de la musique à partir des en-têtes HTTP
     * @return {Promise<void>}
     */
    private async getDurationFromHeaders(): Promise<void> {
        ConsoleTesteur.log('getDurationFromHeaders');
        setTimeout(async () => {// délai pour s'assurer de la generation du cache serveur car Firefox envoi trop vite la requete
            try {
                const response = await fetch(this.DOMElement.src, { method: 'GET', headers: { 'X-Metadata-Only': 'true' } });
                if (!response.ok) {
                    console.error('Failed to fetch metadata:', response.statusText);
                    return;
                }
                const contentDuration = (await response.json()).duration;
                ConsoleTesteur.log('Content-Duration from headers:', contentDuration);
                if (contentDuration) {
                    this.duration = Number.parseFloat(contentDuration);
                }
            } catch (error) {
                console.error('Error fetching Content-Duration:', error);
            }
        }, 500);


    }

    public play() {
        ConsoleTesteur.log('play_action');

        this.DOMElement.addEventListener('error', (e) => this.handleAudioError(e));
        this.DOMElement.addEventListener('playing', () => this.getDurationFromHeaders());

        if (this.fadeIn) {
            this.addFadeIn();
        }

        if (this.fadeOut) {
            this.boundEventFadeOut = this.eventFadeOut.bind(this);
            this.DOMElement.addEventListener('loadedmetadata', () => {
                this.DOMElement.addEventListener('timeupdate', this.boundEventFadeOut!);
            });
            this.DOMElement.addEventListener('ended', () => this.eventDeleteFadeOut());
        } else {
            this.boundEventFadeOut = this.eventDeleteNoFadeOut.bind(this);
            this.DOMElement.addEventListener('ended', this.boundEventFadeOut);
            this.DOMElement.addEventListener('ended', this.disactiveButtonPlaylist.bind(this));
        }
        ConsoleTesteur.info(`▶️ Play ${this.idPlaylist} ${this.isSlave()}`);

        this.DOMElement.play();
    }

    private disactiveButtonPlaylist() {
        const buttonPlaylist = ButtonPlaylistFinder.search(this.idPlaylist);
        if (buttonPlaylist) {
            buttonPlaylist.disactive();
        }
    }

    /**
     * Vérifie si la playlist doit être en boucle
     * @returns boolean
     */
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
        if (this.fadeInGoing) {
            ConsoleCustom.log('ignore fade out if fade in not finished');
            return // ignore fade out if fade in not finished
        }

        let typeFade = Model.default.FadeSelector.selectTypeFade(this.fadeOutType)
        let audioFade = new AudioFadeManager(this, typeFade, false, () => {
            this.levelFade = 1;
        });
        audioFade.setDuration(this.fadeOutDuration);
        audioFade.start();
    }

    private isSlave(): boolean {
        return SharedSoundBoardUtil.isSlavePage()
    }

    private eventFadeOut() {
        const durationRemaining = this.calculTimeRemaining();
        if (durationRemaining <= this.fadeOutDuration && this.fadeOut) {
            ConsoleTesteur.info(`eventFadeOut triggered durationRemaining ${durationRemaining}`);

            if (this.boundEventFadeOut) {
                this.DOMElement.removeEventListener('timeupdate', this.boundEventFadeOut);
            }
            this.addFadeOut();
            this.startIfLooped();
        }
    }

    private startIfLooped() {
        ConsoleTesteur.log('startIfLooped');
        const buttonPlaylist = ButtonPlaylistFinder.search(this.idPlaylist);
        if (!buttonPlaylist) {
            return;
        }
        if (this.checkLoop()) {
            ConsoleTesteur.log("loopOrStop => SoundBoardManager.createPlaylistLink");
            this.applyDelay(() => {
                SoundBoardManager.createPlaylistLink(buttonPlaylist);
            })

        }
    }

    private calculTimeRemaining(): number {
        if (this.duration !== null) {
            return this.duration - this.DOMElement.currentTime;
        }
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
                ConsoleTesteur.log("applyDelay callback: ");
                const buttonPlaylist = ButtonPlaylistFinder.search(this.idPlaylist);
                if (buttonPlaylist && buttonPlaylist.isActive() && this.butonPlaylistToken == buttonPlaylist.getToken()) {
                    callback()
                }
            }, Time.get_seconds(delay));
        } else {
            callback();
        }
    }

    private eventDeleteFadeOut() {
        ConsoleCustom.log('eventDeleteFadeOut');
        if (this.boundEventFadeOut) {
            this.DOMElement.removeEventListener('timeupdate', this.boundEventFadeOut);
        }
        this.DOMElement.remove();
    }

    private eventDeleteNoFadeOut() {
        ConsoleCustom.log('eventDeleteNoFadeOut');
        this.DOMElement.remove();
        this.startIfLooped();
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
            if (audioElement.error && audioElement.error.code === 4) { // => ERROR 404
                // Log toutes les informations disponibles
                ConsoleTraceServeur.error('handleAudioError', audioElement.error.code, audioElement.error.message, this.idPlaylist, this.baseUrl, audioElement.src);

                const buttonPlaylist = ButtonPlaylistFinder.search(this.idPlaylist) as ButtonPlaylist;
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

