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
    private static readonly ENDED_CLEANUP_DELAY_MS = 35;
    DOMElement: HTMLAudioElement
    idPlaylist: string = '';
    playlistType: string = '';
    defaultVolume: number | null = null;
    levelFade: number = 1;
    durationRemainingTriggerNextMusic: number = 0;
    fadeInOnGoing: boolean = false;
    fadeInType: string = 'linear';
    fadeInDuration: number = 0;
    fadeOutType: string = 'linear';
    playlistLoop: boolean = false;
    fadeOutDuration: number = 0;
    delay: number = 0;
    butonPlaylistToken: string | null = null;
    fadeInGoing: boolean = false;
    baseUrl: string = ''; // url of playlist to stream music
    WebSocketActive: boolean = false; // user has websocket connection to command shared soundboard
    duration: number | null = null;
    fadeOffOnStopDuration: number = 0;
    fadeOffOnStopType: string = 'linear';
    private boundEventEnd: (() => void) | null = null;
    private nextLoopStarted: boolean = false;
    private fadeOutDeferredToEnded: boolean = false;


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
        this.fadeInType = dto.fadeInType;
        this.fadeInDuration = dto.fadeInDuration;
        this.fadeOutType = dto.fadeOutType;
        this.fadeOutDuration = dto.fadeOutDuration;
        this.playlistType = dto.playlistType;
        this.idPlaylist = dto.idPlaylist;
        this.playlistLoop = dto.playlistLoop;
        this.delay = dto.delay;
        this.baseUrl = dto.baseUrl;
        this.durationRemainingTriggerNextMusic = dto.durationRemainingTriggerNextMusic;
        this.fadeOffOnStopDuration = dto.fadeOffOnStopDuration;
        this.fadeOffOnStopType = dto.fadeOffOnStopType;
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
        ConsoleTesteur.log(`delete_action ${this.idPlaylist}`);
        const buttonPlaylist = ButtonPlaylistFinder.search(this.idPlaylist) as ButtonPlaylist;
        buttonPlaylist.disactive();
        this.addFadeOutOnStop(() => {
            this.removeDomElement();
        });
        this.callAPIToStop();
    }

    private addFadeOutOnStop(callback: () => void) {
        ConsoleCustom.log('addFadeOutOnStop event');
        if (this.fadeOffOnStopType === 'disabled') {
            callback();
            return;
        }

        if (this.fadeInGoing) {
            ConsoleCustom.log('ignore fade out if fade in not finished');
            callback();
            return // ignore fade out if fade in not finished
        }

        ConsoleCustom.log(`start fade off on stop ${this.fadeOffOnStopType} ${this.fadeOffOnStopDuration}`);
        const typeFade = Model.default.FadeSelector.selectTypeFade(this.fadeOffOnStopType)
        const audioFade = new AudioFadeManager(this, typeFade, false, callback);
        audioFade.setDuration(this.fadeOffOnStopDuration);
        audioFade.start();
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

        const buttonPlaylist = ButtonPlaylistFinder.search(this.idPlaylist);
        if (!buttonPlaylist?.isActive()) {
            ConsoleTesteur.log(`play_action skipped because playlist is not active ${this.idPlaylist}`);
            this.removeDomElement();
            return;
        }

        this.nextLoopStarted = false;

        this.DOMElement.addEventListener('error', (e) => {
            this.handleAudioError(e);
        });

        this.DOMElement.addEventListener('playing', () => {
            this.getDurationFromHeaders();
        });

        if (this.fadeInType !== 'disabled') {
            this.addFadeIn();
        }

        if (this.durationRemainingTriggerNextMusic > 0) {
            this.boundEventEnd = this.eventFadeOut.bind(this);
            this.DOMElement.addEventListener('loadedmetadata', () => {
                this.DOMElement.addEventListener('timeupdate', this.boundEventEnd!);
            });
            this.DOMElement.addEventListener('ended', () => {
                // Slightly defer cleanup to avoid cutting the very end on some browsers/codecs.
                globalThis.setTimeout(() => this.eventDeleteFadeOut(), MusicElement.ENDED_CLEANUP_DELAY_MS);
            }, { once: true });
        } else {
            this.boundEventEnd = () => {
                this.eventDeleteNoFadeOut.bind(this)();
                this.disactiveButtonPlaylist.bind(this)();
            };
            this.DOMElement.addEventListener('ended', () => {
                // Slightly defer cleanup to avoid cutting the very end on some browsers/codecs.
                globalThis.setTimeout(() => this.boundEventEnd!(), MusicElement.ENDED_CLEANUP_DELAY_MS);
            }, { once: true });
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

    /**
     * add fade in effect to the music element
     * 
     * return void 
     */
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
            const duration = this.getTrackDuration() || 0;
            if (this.fadeInDuration * 2 > duration) { // fade in duration is too long for the track duration, so we skip the fade in
                ConsoleTesteur.info('addFadeIn skipped because fade in duration is too long for the track duration');
                this.levelFade = 1;
                this.fadeInGoing = false;
                audioFade.skip();
            } else {
                let time = Date.now();
                while (this.DOMElement.readyState != 2) {
                    if (time + 1 < Date.now()) {
                        break;
                    }
                }
                ConsoleTesteur.info('addFadeIn trigger start');
                audioFade.start();
            }
        })

    }

    public addFadeOut(): boolean {
        ConsoleCustom.log('addFadeOut');
        if (this.fadeInGoing) {
            ConsoleCustom.log('ignore fade out if fade in not finished');
            return false; // ignore fade out if fade in not finished
        }

        let typeFade = Model.default.FadeSelector.selectTypeFade(this.fadeOutType)
        let audioFade = new AudioFadeManager(this, typeFade, false, () => {
            this.levelFade = 1;
        });
        audioFade.setDuration(this.fadeOutDuration);
        audioFade.start();

        return true;
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

            if (this.shouldDeferFadeOutToEnded()) {
                this.fadeOutDeferredToEnded = true;
                ConsoleTesteur.info('defer fade out to ended because track is shorter than trigger + fade out durations');
                return;
            }

            if (this.fadeOutType !== 'disabled') {
                this.addFadeOut();
            }
            this.startIfLooped();
        }
    }

    /**
     * Starts the music element if it is set to loop.
     * 
     * @returns void
     */
    private startIfLooped() {
        ConsoleTesteur.log('startIfLooped');
        if (this.nextLoopStarted) {
            return;
        }

        const buttonPlaylist = ButtonPlaylistFinder.search(this.idPlaylist);
        if (!buttonPlaylist) {
            return;
        }
        if (this.checkLoop()) {
            this.nextLoopStarted = true;
            ConsoleTesteur.log("loopOrStop => SoundBoardManager.createPlaylistLink");
            this.applyDelay(() => {
                SoundBoardManager.createPlaylistLink(buttonPlaylist);
            })

        }
    }

    /**
     * Calculates the remaining time of the music element.
     * 
     * @returns number
     */
    private calculTimeRemaining(): number {
        if (this.duration !== null) {
            return this.duration - this.DOMElement.currentTime;
        }
        return this.DOMElement.duration - this.DOMElement.currentTime;
    }

    /**
     * Calculates a random delay time based on the configured delay.
     * 
     * @returns number
     */
    private getTimeDelay(): number {
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

        if (this.fadeOutDeferredToEnded) {
            this.fadeOutDeferredToEnded = false;
            this.startIfLooped();
        }
    }

    private shouldDeferFadeOutToEnded(): boolean {
        if (this.fadeOutType === 'disabled') {
            return false;
        }

        const trackDuration = this.getTrackDuration();
        if (trackDuration === null) {
            return false;
        }

        const overlapWindow = this.durationRemainingTriggerNextMusic + this.fadeOutDuration;
        return trackDuration <= overlapWindow;
    }

    private getTrackDuration(): number | null {
        if (this.duration !== null && Number.isFinite(this.duration) && this.duration > 0) {
            return this.duration;
        }

        if (Number.isFinite(this.DOMElement.duration) && this.DOMElement.duration > 0) {
            return this.DOMElement.duration;
        }

        return null;
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

            if (audioElement.error?.code === 4) { // => ERROR 404
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

