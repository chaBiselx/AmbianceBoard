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
import { IAudioAdapter } from '@/modules/Audio/IAudioAdapter';
import SoundEventBus from '@/modules/Script/SoundEventBus';





class MusicElement {
    private static readonly previewInstances = new Set<MusicElement>();
    readonly preview: boolean;
    private disposed = false;
    private removed = false;
    private trackName = '';
    private readonly previewTimers = new Set<ReturnType<typeof setTimeout>>();
    private readonly previewFades = new Set<AudioFadeManager>();
    private readonly previewListeners: Array<{ type: string; listener: EventListener }> = [];
    private readonly metadataAbort = new AbortController();
    private static readonly ENDED_CLEANUP_DELAY_MS = 35;
    private readonly audioAdapter: IAudioAdapter;
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


    constructor(audioAdapter: IAudioAdapter, dto: MusicElementDTO) {
        this.audioAdapter = audioAdapter;
        this.preview = dto.preview === true;
        if (this.preview) MusicElement.previewInstances.add(this);
        this.initializeFromDTO(dto);

        if (!this.preview && Cookie.get('WebSocketToken') != null) {
            this.WebSocketActive = true;
        }
    }

    static getPreviewElements(): MusicElement[] {
        return [...this.previewInstances].filter(element => !element.removed);
    }

    static disposePreview(): void {
        for (const element of this.previewInstances) element.dispose();
    }

    getPlaybackState(): { name: string; currentTime: number; duration: number | null } {
        return { name: this.trackName, currentTime: this.audioAdapter.getCurrentTime(), duration: this.getTrackDuration() };
    }

    dispose(): void {
        if (this.disposed) return;
        this.disposed = true;
        this.metadataAbort.abort();
        for (const timer of this.previewTimers) clearTimeout(timer);
        for (const fade of this.previewFades) fade.cancel();
        for (const { type, listener } of this.previewListeners) this.audioAdapter.removeEventListener(type, listener);
        this.previewTimers.clear();
        this.previewFades.clear();
        this.previewListeners.length = 0;
        this.audioAdapter.stop?.();
        this.audioAdapter.remove();
        MusicElement.previewInstances.delete(this);
    }

    private defer(callback: () => void, milliseconds: number): void {
        const timer = globalThis.setTimeout(() => {
            this.previewTimers.delete(timer);
            if (!this.disposed) {
                callback();
                if (this.preview && this.removed && this.previewTimers.size === 0) this.dispose();
            }
        }, milliseconds);
        if (this.preview) this.previewTimers.add(timer);
    }

    private listen(type: string, listener: EventListener, options?: AddEventListenerOptions): void {
        this.audioAdapter.addEventListener(type, listener, options);
        if (this.preview) this.previewListeners.push({ type, listener });
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
        this.audioAdapter.setDatasetValue('defaultvolume', this.defaultVolume.toString());
    }

    public addToDOM(): this {
        const audioElementDiv = document.getElementById(Config.SOUNDBOARD_DIV_ID_PLAYERS) as HTMLElement;
        this.audioAdapter.appendTo(audioElementDiv);
        this.audioAdapter.setPreload('metadata');


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
        if (!this.preview) SoundEventBus.emit('music:stopped', { playlistId: this.idPlaylist, token: this.butonPlaylistToken });
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
        if (this.preview) this.previewFades.add(audioFade);
        audioFade.setDuration(this.fadeOffOnStopDuration);
        audioFade.start();
    }

    private removeDomElement() {
        this.removed = true;
        if (this.preview) this.audioAdapter.stop?.();
        if (this.boundEventEnd) {
            this.audioAdapter.removeEventListener('timeupdate', this.boundEventEnd);
        }
        this.audioAdapter.remove();
        if (this.preview && !ButtonPlaylistFinder.search(this.idPlaylist)?.isActive()) this.dispose();
    }



    public setSpecificMusic(baseUrl: string) {
        this.baseUrl = baseUrl;
        this.audioAdapter.setDatasetValue('baseurl', this.baseUrl);
        this.audioAdapter.setSource(this.baseUrl);
    }

    /**
     * Récupère la durée de la musique à partir des en-têtes HTTP
     */
    private getDurationFromHeaders(): void {
        ConsoleTesteur.log('getDurationFromHeaders');

        this.defer(async () => {
            try {
            const response = await fetch(this.audioAdapter.getSource(), { method: 'GET', headers: { 'X-Metadata-Only': 'true' }, ...(this.preview ? { signal: this.metadataAbort.signal } : {}) });
                if (!response.ok) {
                    console.error('Failed to fetch metadata:', response.statusText);
                    return;
                }

                const metadata = await response.json();
                if (this.disposed) return;
                const contentDuration = metadata.duration;
                if (this.preview) this.trackName = metadata.name ?? '';
                ConsoleTesteur.log('Content-Duration from headers:', contentDuration);
                if (contentDuration) {
                    this.duration = Number.parseFloat(contentDuration);
                }
            } catch (error) {
                if (this.disposed) return;
                console.error('Error fetching Content-Duration:', error);
            }
        }, 500);


    }

    public play() {
        if (this.disposed) return;
        ConsoleTesteur.log('play_action');

        const buttonPlaylist = ButtonPlaylistFinder.search(this.idPlaylist);
        if (!buttonPlaylist?.isActive()) {
            ConsoleTesteur.log(`play_action skipped because playlist is not active ${this.idPlaylist}`);
            this.removeDomElement();
            return;
        }

        this.nextLoopStarted = false;

        this.listen('error', (e) => {
            this.handleAudioError(e);
        });

        this.listen('playing', () => {
            this.getDurationFromHeaders();
        });

        if (this.fadeInType !== 'disabled') {
            this.addFadeIn();
        }

        if (this.durationRemainingTriggerNextMusic > 0) {
            this.boundEventEnd = this.eventFadeOut.bind(this);
            this.listen('loadedmetadata', () => {
                this.listen('timeupdate', this.boundEventEnd!);
            });
            this.listen('ended', () => {
                // Slightly defer cleanup to avoid cutting the very end on some browsers/codecs.
                this.defer(() => this.eventDeleteFadeOut(), MusicElement.ENDED_CLEANUP_DELAY_MS);
            }, { once: true });
        } else {
            this.boundEventEnd = () => {
                this.eventDeleteNoFadeOut.bind(this)();
                this.disactiveButtonPlaylist.bind(this)();
            };
            this.listen('ended', () => {
                // Slightly defer cleanup to avoid cutting the very end on some browsers/codecs.
                this.defer(() => this.boundEventEnd!(), MusicElement.ENDED_CLEANUP_DELAY_MS);
            }, { once: true });
        }
        ConsoleTesteur.info(`▶️ Play ${this.idPlaylist} ${this.isSlave()}`);

        this.listen('ended', () => {
            if (!this.preview) SoundEventBus.emit('music:ended', { playlistId: this.idPlaylist, token: this.butonPlaylistToken });
        }, { once: true });

        void this.audioAdapter.play().catch((error: unknown) => {
            if (this.disposed) return;
            if (this.preview) {
                this.failPreview();
                return;
            }
            if (error && typeof error === 'object' && 'name' in error && error.name === 'AbortError') {
                return;
            }
            ConsoleTraceServeur.error('playAudioError', error, this.idPlaylist);
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
        if (this.preview) this.previewFades.add(audioFade);
        audioFade.setDuration(this.fadeInDuration);
        this.listen('playing', () => {
            const duration = this.getTrackDuration() || 0;
            if (this.fadeInDuration * 2 > duration) { // fade in duration is too long for the track duration, so we skip the fade in
                ConsoleTesteur.info('addFadeIn skipped because fade in duration is too long for the track duration');
                this.levelFade = 1;
                this.fadeInGoing = false;
                audioFade.skip();
            } else {
                let time = Date.now();
                while (this.audioAdapter.getReadyState() != 2) {
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
        if (this.preview) this.previewFades.add(audioFade);
        audioFade.setDuration(this.fadeOutDuration);
        audioFade.start();

        return true;
    }

    private isSlave(): boolean {
        if (this.preview) return false;
        return SharedSoundBoardUtil.isSlavePage()
    }

    private eventFadeOut() {
        const durationRemaining = this.calculTimeRemaining();

        if (durationRemaining <= this.durationRemainingTriggerNextMusic) {
            ConsoleTesteur.info(`eventFadeOut triggered durationRemaining ${durationRemaining}`);
            if (this.boundEventEnd) {
                this.audioAdapter.removeEventListener('timeupdate', this.boundEventEnd);
            }

            if (this.fadeOutType === 'disabled' || this.shouldDeferFadeOutToEnded()) {
                this.fadeOutDeferredToEnded = true;
                ConsoleTesteur.info('defer playlist transition until ended');
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
        if (this.disposed) return;
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
            const delaiFadeOff = this.fadeOutDeferredToEnded ? 0 : this.fadeOutDuration;
            
            this.applyDelay(
                () => { SoundBoardManager.createPlaylistLink(buttonPlaylist); },
                delaiFadeOff
            );

        }
    }

    /**
     * Calculates the remaining time of the music element.
     * 
     * @returns number
     */
    private calculTimeRemaining(): number {
        if (this.duration !== null) {
            return this.duration - this.audioAdapter.getCurrentTime();
        }
        return this.audioAdapter.getDuration() - this.audioAdapter.getCurrentTime();
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

    private applyDelay(callback: () => void, timeFadeOff: number = 0) {
        ConsoleTesteur.log(`applyDelay => ${this.delay} ${typeof this.delay}`);
        if (this.delay > 0) {
            const delay = this.getTimeDelay();
            const delaiAjusted = delay + timeFadeOff;
            ConsoleTesteur.log("delay: " + delay + " delaiAjusted: " + delaiAjusted);
            this.defer(() => {
                ConsoleTesteur.log("applyDelay callback: ");
                const buttonPlaylist = ButtonPlaylistFinder.search(this.idPlaylist);
                if (buttonPlaylist && buttonPlaylist.isActive() && this.butonPlaylistToken == buttonPlaylist.getToken()) {
                    callback()
                }
            }, Time.get_seconds(delaiAjusted));
        } else {
            callback();
        }
    }

    private eventDeleteFadeOut() {
        ConsoleCustom.log('eventDeleteFadeOut');
        this.removeDomElement();

        if (this.fadeOutDeferredToEnded) {
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

        const duration = this.audioAdapter.getDuration();
        if (Number.isFinite(duration) && duration > 0) {
            return duration;
        }

        return null;
    }

    private eventDeleteNoFadeOut() {
        ConsoleCustom.log('eventDeleteNoFadeOut');
        this.removeDomElement();
        this.startIfLooped();
    }

    private callAPIToStop() {
        if (this.preview) return;
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

    public setVolume(volume: number): void {
        this.audioAdapter.setVolume(volume);
    }

    private handleAudioError(_: Event) {
        if (this.disposed) return;
        if (this.preview) {
            this.failPreview();
            return;
        }
        const audioError = this.audioAdapter.getError();
        if (audioError?.code === 4) { // => ERROR 404
            // Log toutes les informations disponibles
            ConsoleTraceServeur.error('handleAudioError', audioError.code, audioError.message, this.idPlaylist, this.baseUrl, this.audioAdapter.getSource());

            const buttonPlaylist = ButtonPlaylistFinder.search(this.idPlaylist) as ButtonPlaylist;
            buttonPlaylist.disactive();
            Notification.createClientNotification({ message: 'Aucune musique n\'est presente dans cette playlist', type: 'danger', duration: 2000 });
            this.addSuggestEditMode();
            this.audioAdapter.remove();
        }
    }

    private addSuggestEditMode(): void {
        const btnEditMode = document.getElementById(`btn-soundboard-edit-mode`);
        if(btnEditMode) {
            Notification.createClientNotification({ message: 'Passer en mode édition pour ajouter des sons', type: 'info', duration: 2000 });
        }

    }

    private failPreview(): void {
        const button = ButtonPlaylistFinder.search(this.idPlaylist);
        if (button) {
            button.dataset.previewError = 'true';
            button.disactive();
        }
        this.dispose();
    }

}


export { MusicElement };
