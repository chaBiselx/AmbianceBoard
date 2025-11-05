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
import Time from "@/modules/Util/Time";
import ConsoleTesteur from '@/modules/General/ConsoleTesteur';
import { MusicElementDTO } from '@/modules/MusicElementFactory';





class MusicElement {
    DOMElement: HTMLAudioElement
    idPlaylist: string = '';
    playlistType: string = '';
    defaultVolume: number = 1;
    levelFade: number = 1;
    durationRemainingTriggerNextMusic: number = 0;
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


    constructor(audioElement: HTMLAudioElement, dto: MusicElementDTO) {
        this.DOMElement = audioElement;
        this.initializeFromDTO(dto);

        if (Cookie.get('WebSocketToken') != null) {
            this.WebSocketActive = true;
        }
    }

    /**
     * Initialise les propriétés de MusicElement à partir du DTO
     */
    private initializeFromDTO(dto: MusicElementDTO): void {
        this.butonPlaylistToken = dto.butonPlaylistToken;
        this.defaultVolume = dto.defaultVolume;
        this.fadeIn = dto.fadeIn;
        this.fadeInType = dto.fadeInType;
        this.fadeInDuration = dto.fadeInDuration;
        this.fadeOut = dto.fadeOut;
        this.fadeOutType = dto.fadeOutType;
        this.fadeOutDuration = dto.fadeOutDuration;
        this.playlistType = dto.playlistType;
        this.idPlaylist = dto.idPlaylist;
        this.playlistLoop = dto.playlistLoop;
        this.delay = dto.delay;
        this.baseUrl = dto.baseUrl;
        this.durationRemainingTriggerNextMusic = dto.durationRemainingTriggerNextMusic;
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
        this.removeDomElement();
        this.callAPIToStop();
    }

    private removeDomElement() {
        if (this.boundEventEnd) {
            this.DOMElement.removeEventListener('timeupdate', this.boundEventEnd);
        }
        this.DOMElement.remove();
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
        this.DOMElement.addEventListener('error', (e) => {
            this.handleAudioError(e);
        });
        
        this.DOMElement.addEventListener('playing', () => {
            this.getDurationFromHeaders();
        });

        if (this.fadeIn) {
            this.addFadeIn();
        }

        if (this.durationRemainingTriggerNextMusic > 0) {
            this.boundEventEnd = this.eventFadeOut.bind(this);
            this.DOMElement.addEventListener('loadedmetadata', () => {
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
        ConsoleTesteur.info('ajout event addFadeIn');
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
            ConsoleTesteur.info('addFadeIn trigger start');
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
        
        if (durationRemaining <= this.durationRemainingTriggerNextMusic) {
            ConsoleTesteur.info(`eventFadeOut triggered durationRemaining ${durationRemaining}`);
            if (this.boundEventEnd) {
                this.DOMElement.removeEventListener('timeupdate', this.boundEventEnd);
            }
            if( this.fadeOut ){
                this.addFadeOut();
            }
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


export { MusicElement };

