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
    private boundEventEnd: (() => void) | null = null;


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
        console.info('MusicElement.delete - Start', {
            playlistId: this.idPlaylist,
            hasBoundEventEnd: !!this.boundEventEnd,
            timestamp: Date.now()
        });
        
        const buttonPlaylist = ButtonPlaylistFinder.search(this.idPlaylist) as ButtonPlaylist;
        buttonPlaylist.disactive();
        this.removeDomElement();
        this.callAPIToStop();
        
        console.info('MusicElement.delete - Complete', {
            playlistId: this.idPlaylist,
            timestamp: Date.now()
        });
    }

    private removeDomElement() {
        console.info('removeDomElement - Start', {
            playlistId: this.idPlaylist,
            hasBoundEventEnd: !!this.boundEventEnd,
            timestamp: Date.now()
        });
        
        if (this.boundEventEnd) {
            this.DOMElement.removeEventListener('timeupdate', this.boundEventEnd);
        }
        this.DOMElement.remove();
        
        console.info('removeDomElement - Complete', {
            playlistId: this.idPlaylist,
            timestamp: Date.now()
        });
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
        console.info('getDurationFromHeaders - Start', {
            playlistId: this.idPlaylist,
            src: this.DOMElement.src,
            timestamp: Date.now()
        });
        
        setTimeout(async () => {// délai pour s'assurer de la generation du cache serveur car Firefox envoi trop vite la requete
            try {
                console.info('getDurationFromHeaders - Fetch attempt', {
                    playlistId: this.idPlaylist,
                    url: this.DOMElement.src,
                    timestamp: Date.now()
                });
                
                const response = await fetch(this.DOMElement.src, { method: 'GET', headers: { 'X-Metadata-Only': 'true' } });
                
                console.info('getDurationFromHeaders - Fetch response received', {
                    playlistId: this.idPlaylist,
                    status: response.status,
                    ok: response.ok,
                    headers: Object.fromEntries(response.headers.entries()),
                    timestamp: Date.now()
                });
                
                if (!response.ok) {
                    console.error('getDurationFromHeaders - Fetch failed', {
                        playlistId: this.idPlaylist,
                        status: response.status,
                        statusText: response.statusText,
                        timestamp: Date.now()
                    });
                    console.error('Failed to fetch metadata:', response.statusText);
                    return;
                }
                
                const contentDuration = (await response.json()).duration;
                ConsoleTesteur.log('Content-Duration from headers:', contentDuration);
                console.info('getDurationFromHeaders - Success', {
                    playlistId: this.idPlaylist,
                    duration: contentDuration,
                    timestamp: Date.now()
                });
                
                if (contentDuration) {
                    this.duration = Number.parseFloat(contentDuration);
                }
            } catch (error) {
                console.error('getDurationFromHeaders - Exception caught', {
                    playlistId: this.idPlaylist,
                    error: error instanceof Error ? error.message : String(error),
                    errorName: error instanceof Error ? error.name : 'Unknown',
                    errorStack: error instanceof Error ? error.stack : undefined,
                    timestamp: Date.now()
                });
                console.error('Error fetching Content-Duration:', error);
            }
        }, 500);


    }

    public play() {
        ConsoleTesteur.log('play_action');
        console.info('MusicElement.play - Start', {
            playlistId: this.idPlaylist,
            playlistType: this.playlistType,
            fadeIn: this.fadeIn,
            fadeOut: this.fadeOut,
            isSlave: this.isSlave(),
            src: this.DOMElement.src,
            timestamp: Date.now()
        });

        this.DOMElement.addEventListener('error', (e) => {
            console.error('MusicElement.play - Audio error event', {
                playlistId: this.idPlaylist,
                timestamp: Date.now()
            });
            this.handleAudioError(e);
        });
        
        this.DOMElement.addEventListener('playing', () => {
            console.info('MusicElement.play - Playing event triggered', {
                playlistId: this.idPlaylist,
                timestamp: Date.now()
            });
            this.getDurationFromHeaders().catch(err => {
                console.error('MusicElement.play - getDurationFromHeaders promise rejected', {
                    playlistId: this.idPlaylist,
                    error: err instanceof Error ? err.message : String(err),
                    timestamp: Date.now()
                });
            });
        });

        if (this.fadeIn) {
            this.addFadeIn();
        }

        if (this.fadeOut) {
            this.boundEventEnd = this.eventFadeOut.bind(this);
            this.DOMElement.addEventListener('loadedmetadata', () => {
                console.info('MusicElement.play - Loadedmetadata event', {
                    playlistId: this.idPlaylist,
                    duration: this.DOMElement.duration,
                    timestamp: Date.now()
                });
                this.DOMElement.addEventListener('timeupdate', this.boundEventEnd!);
            });
            this.DOMElement.addEventListener('ended', () => this.eventDeleteFadeOut());
        } else {
            this.boundEventEnd = () => { 
                this.eventDeleteNoFadeOut.bind(this)(); 
                this.disactiveButtonPlaylist.bind(this)();
            };
            this.DOMElement.addEventListener('ended', this.boundEventEnd);
        }
        ConsoleTesteur.info(`▶️ Play ${this.idPlaylist} ${this.isSlave()}`);

        console.info('MusicElement.play - About to call play()', {
            playlistId: this.idPlaylist,
            readyState: this.DOMElement.readyState,
            timestamp: Date.now()
        });
        
        this.DOMElement.play().catch(err => {
            console.error('MusicElement.play - play() promise rejected', {
                playlistId: this.idPlaylist,
                error: err instanceof Error ? err.message : String(err),
                errorName: err instanceof Error ? err.name : 'Unknown',
                timestamp: Date.now()
            });
        });
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
        ConsoleTesteur.info('ajout event addFadeIn');
        console.info('addFadeIn - Start', {
            playlistId: this.idPlaylist,
            fadeInType: this.fadeInType,
            fadeInDuration: this.fadeInDuration,
            timestamp: Date.now()
        });

        this.levelFade = 0;

        this.fadeInGoing = true;

        let typeFade = Model.default.FadeSelector.selectTypeFade(this.fadeInType)

        let audioFade = new AudioFadeManager(this, typeFade, true, () => {
            console.info('addFadeIn - Callback triggered', {
                playlistId: this.idPlaylist,
                timestamp: Date.now()
            });
            this.levelFade = 1;
            this.fadeInGoing = false;
        });
        audioFade.setDuration(this.fadeInDuration);
        this.DOMElement.addEventListener('playing', () => {
            console.info('addFadeIn - Playing event in fade handler', {
                playlistId: this.idPlaylist,
                readyState: this.DOMElement.readyState,
                timestamp: Date.now()
            });
            
            let time = Date.now();
            while (this.DOMElement.readyState != 2) {
                if (time + 1 < Date.now()) {
                    break;
                }
            }
            ConsoleTesteur.info('addFadeIn trigger start');
            console.info('addFadeIn - Starting fade', {
                playlistId: this.idPlaylist,
                readyState: this.DOMElement.readyState,
                timestamp: Date.now()
            });
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
        console.info('eventFadeOut - Checking', {
            playlistId: this.idPlaylist,
            durationRemaining,
            fadeOutDuration: this.fadeOutDuration,
            shouldTriggerFadeOut: durationRemaining <= this.fadeOutDuration && this.fadeOut,
            timestamp: Date.now()
        });
        
        if (durationRemaining <= this.fadeOutDuration && this.fadeOut) {
            ConsoleTesteur.info(`eventFadeOut triggered durationRemaining ${durationRemaining}`);
            console.info('eventFadeOut - Triggering fade out', {
                playlistId: this.idPlaylist,
                durationRemaining,
                timestamp: Date.now()
            });

            if (this.boundEventEnd) {
                this.DOMElement.removeEventListener('timeupdate', this.boundEventEnd);
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
        this.removeDomElement();
    }

    private eventDeleteNoFadeOut() {
        ConsoleCustom.log('eventDeleteNoFadeOut');
        this.removeDomElement();
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
        console.error('handleAudioError - Event triggered', {
            playlistId: this.idPlaylist,
            hasTarget: !!event.target,
            timestamp: Date.now()
        });
        
        if (event.target && event.target instanceof HTMLAudioElement) {
            const audioElement = event.target;
            
            console.error('handleAudioError - Audio element error details', {
                playlistId: this.idPlaylist,
                baseUrl: this.baseUrl,
                src: audioElement.src,
                errorCode: audioElement.error?.code,
                errorMessage: audioElement.error?.message,
                networkState: audioElement.networkState,
                readyState: audioElement.readyState,
                timestamp: Date.now()
            });
            
            if (audioElement.error && audioElement.error.code === 4) { // => ERROR 404
                // Log toutes les informations disponibles
                ConsoleTraceServeur.error('handleAudioError', audioElement.error.code, audioElement.error.message, this.idPlaylist, this.baseUrl, audioElement.src);

                const buttonPlaylist = ButtonPlaylistFinder.search(this.idPlaylist) as ButtonPlaylist;
                buttonPlaylist.disactive();
                Notification.createClientNotification({ message: 'Aucune musique n\'est presente dans cette playlist', type: 'danger', duration: 2000 });
                event.target.remove();
            } else if (audioElement.error) {
                console.error('handleAudioError - Non-404 error', {
                    playlistId: this.idPlaylist,
                    errorCode: audioElement.error.code,
                    errorMessage: audioElement.error.message,
                    timestamp: Date.now()
                });
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

