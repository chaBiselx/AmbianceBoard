import Config from '@/modules/Config';
import Notification from '@/modules/Notifications';

import { ButtonPlaylist, ButtonPlaylistFinder } from '@/modules/ButtonPlaylist';
import * as Model from '@/modules/FadeStartegy';
import AudioFadeManager from '@/modules/AudioFadeManager';
import { SoundBoardManager } from '@/modules/SoundBoardManager';
import Cookie from '@/modules/Cookie';

const TRUE = 'True';//TODO fix type soundboard_read


class MusicElement {
    DOMElement: HTMLAudioElement
    idPlaylist: string = '';
    playlistType: string = '';
    defaultVolume: number = 1;
    autoplay: boolean = true;
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
    isSlave: boolean = false; // is manuplated by websocket (shared soundboard)


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
            this.defaultVolume = parseFloat(this.DOMElement.dataset.defaultvolume);
        }
        if (this.DOMElement.dataset.fadein) {
            this.fadeIn = this.DOMElement.dataset.fadein == "true";
        }
        if (this.DOMElement.dataset.fadeintype) {
            this.fadeInType = this.DOMElement.dataset.fadeintype;
        }
        if (this.DOMElement.dataset.fadeinduration) {
            this.fadeInDuration = parseFloat(this.DOMElement.dataset.fadeinduration);
        }
        if (this.DOMElement.dataset.fadeout) {
            this.fadeOut = this.DOMElement.dataset.fadeout == "true";
        }
        if (this.DOMElement.dataset.fadeouttype) {
            this.fadeOutType = this.DOMElement.dataset.fadeouttype;
        }
        if (this.DOMElement.dataset.fadeoutduration) {
            this.fadeOutDuration = parseFloat(this.DOMElement.dataset.fadeoutduration);
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
            this.delay = parseFloat(this.DOMElement.dataset.playlistdelay);
        }
        if (this.DOMElement.dataset.baseurl) {
            this.baseUrl = this.DOMElement.dataset.baseurl!;
        }
        if (this.DOMElement.dataset.isslave) {
            this.isSlave = this.DOMElement.dataset.isslave == "true";
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
        if (!this.isSlave) {
            src += "?i=" + Date.now();
        }
        this.DOMElement.src = src;
        this.DOMElement.controls = Config.DEBUG;
        this.DOMElement.autoplay = true;
    }

    public setDefaultVolume(volume: number) {
        this.defaultVolume = volume;
        this.DOMElement.dataset.defaultvolume = this.defaultVolume.toString();
    }

    public addToDOM(): this {
        const audioElementDiv = document.getElementById(Config.SOUNDBOARD_DIV_ID_PLAYERS) as HTMLElement;
        audioElementDiv.appendChild(this.DOMElement);
        return this
    }

    public delete() {
        const buttonPlaylist = ButtonPlaylistFinder.search(this.idPlaylist) as ButtonPlaylist;
        buttonPlaylist.disactive();
        this.DOMElement.remove();

        this.callAPIToStop()
    }

    public setSpecificMusic(baseUrl: string) {
        this.setSlave(true);
        this.baseUrl = baseUrl;
        this.DOMElement.dataset.baseurl = this.baseUrl;
        this.DOMElement.src = this.baseUrl;
    }

    public play() {
        if (Config.DEBUG) console.log('play');
        this.DOMElement.addEventListener('error', this.handleAudioError);

        if (this.fadeIn) {
            this.addFadeIn();
        }

        if (this.fadeOut) {
            this.DOMElement.addEventListener('ended', this.eventDeleteFadeOut);
            this.DOMElement.addEventListener('loadedmetadata', () => {
                this.DOMElement.addEventListener('timeupdate', this.eventFadeOut);
            });

        } else {
            this.DOMElement.addEventListener('ended', this.eventDeleteNoFadeOut);
        }
        this.DOMElement.play();

    }

    public checkLoop(): boolean {
        return this.playlistLoop && !this.isSlave
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
        if (Config.DEBUG) console.log('addFadeOut');
        if (this.fadeInGoing) {
            if (Config.DEBUG) console.log('ignore fade out if fade in not finished');
            return // ignore fade out if fade in not finished
        }

        let typeFade = Model.default.FadeSelector.selectTypeFade(this.fadeInType)
        let audioFade = new AudioFadeManager(this, typeFade, false, () => {
            this.levelFade = 1;
        });
        audioFade.setDuration(this.fadeOutDuration);
        audioFade.start();
    }

    private eventFadeOut(event: Event) {
        if (Config.DEBUG) console.log('eventFadeOut');
        let new_music = new MusicElement(event.target as HTMLAudioElement);
        const timeRemaining = new_music.DOMElement.duration - new_music.DOMElement.currentTime;

        if (timeRemaining <= new_music.fadeOutDuration && new_music.fadeOut) {
            const buttonPlaylist = ButtonPlaylistFinder.search(new_music.idPlaylist);
            if (buttonPlaylist) {


                new_music.DOMElement.removeEventListener('timeupdate', new_music.eventFadeOut);
                new_music.addFadeOut();
                if (new_music.checkLoop()) {
                    if (Config.DEBUG) console.log("eventFadeOut loop");
                    new_music.applyDelay(() => {
                        SoundBoardManager.createPlaylistLink(buttonPlaylist);
                    })
                } else {
                    buttonPlaylist.disactive();
                }
            }
        }
    }

    private getTimeDelay() {
        if (this.delay > 0) {
            return Math.floor(Math.random() * this.delay * 100) / 100;
        }
        return 0;
    }

    private applyDelay(callback: () => void) {
        if (this.delay > 0) {
            const delay = this.getTimeDelay();
            if (Config.DEBUG) console.log("delay: " + delay);
            setTimeout(() => {
                if (Config.DEBUG) console.log("applyDelay callback: ");

                const buttonPlaylist = ButtonPlaylistFinder.search(this.idPlaylist);
                if (buttonPlaylist && buttonPlaylist.isActive() && this.butonPlaylistToken == buttonPlaylist.getToken()) {
                    callback()
                }
            }, delay * 1000);
        } else {
            callback();
        }
    }

    private eventDeleteFadeOut(event: Event) {
        if (Config.DEBUG) console.log('eventDeleteFadeOut');
        let new_music = new MusicElement(event.target as HTMLAudioElement);
        new_music.DOMElement.remove();
    }

    private eventDeleteNoFadeOut(event: Event) {
        if (Config.DEBUG) console.log('eventDeleteNoFadeOut');
        let new_music = new MusicElement(event.target as HTMLAudioElement);
        new_music.DOMElement.remove();
        if (new_music.checkLoop()) {
            const buttonPlaylist = ButtonPlaylistFinder.search(new_music.idPlaylist) as ButtonPlaylist;
            new_music.applyDelay(() => {
                SoundBoardManager.createPlaylistLink(buttonPlaylist);
            })
        } else {
            const buttonPlaylist = ButtonPlaylistFinder.search(new_music.idPlaylist) as ButtonPlaylist;
            buttonPlaylist.disactive();
        }
    }

    private callAPIToStop() {
        if (this.WebSocketActive && !this.isSlave) {
            fetch(this.baseUrl + '/stop', {
                method: 'UPDATE',
                headers: {
                    'X-CSRFToken': Cookie.get('csrftoken')!,
                    'Content-Type': 'application/json',
                },
            }).then((response) => {
                if (Config.DEBUG) console.log('callAPIToStop', response);
            })
        }
    }

    private setDefaultVolumeFromPlaylist(buttonPlaylist: ButtonPlaylist): void {
        if (buttonPlaylist.dataset.playlistVolume) {
            this.setDefaultVolume(buttonPlaylist.getVolume());
        }
    }

    private setFadeInFromPlaylist(buttonPlaylist: ButtonPlaylist): void {
        if (buttonPlaylist.dataset.playlistFadein) {
            this.fadeIn = buttonPlaylist.dataset.playlistFadein == TRUE;
            this.DOMElement.dataset.fadein = this.fadeIn.toString();
        }
        if (buttonPlaylist.dataset.playlistFadeintype) {
            this.fadeInType = buttonPlaylist.dataset.playlistFadeintype;
            this.DOMElement.dataset.fadeintype = this.fadeInType;
        }
        if (buttonPlaylist.dataset.playlistFadeinduration) {
            this.fadeInDuration = parseFloat(buttonPlaylist.dataset.playlistFadeinduration);
            this.DOMElement.dataset.fadeinduration = this.fadeInDuration.toString();
        }
    }

    private setFadeOutFromPlaylist(buttonPlaylist: ButtonPlaylist): void {
        if (buttonPlaylist.dataset.playlistFadeout) {
            this.fadeOut = buttonPlaylist.dataset.playlistFadein == TRUE;
            this.DOMElement.dataset.fadeout = this.fadeOut.toString();
        }
        if (buttonPlaylist.dataset.playlistFadeouttype) {
            this.fadeOutType = buttonPlaylist.dataset.playlistFadeouttype;
            this.DOMElement.dataset.fadeouttype = this.fadeOutType;
        }
        if (buttonPlaylist.dataset.playlistFadeoutduration) {
            this.fadeOutDuration = parseFloat(buttonPlaylist.dataset.playlistFadeoutduration);
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
            this.playlistLoop = buttonPlaylist.dataset.playlistLoop == TRUE;
            this.DOMElement.dataset.playlistloop = this.playlistLoop.toString();
        }
    }

    private setPlaylistDelayFromPlaylist(buttonPlaylist: ButtonPlaylist): void {
        if (buttonPlaylist.dataset.playlistDelay) {
            this.delay = parseFloat(buttonPlaylist.dataset.playlistDelay);
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

    private setSlave(slave: boolean): this {
        this.isSlave = slave;
        this.DOMElement.dataset.isslave = this.isSlave.toString();
        return this
    }

    private handleAudioError(event: Event) {
        if (event.target && event.target instanceof HTMLAudioElement) {
            if (event.target.error && event.target.error.code === 4) { // => ERROR 404
                let new_music = new MusicElement(event.target);

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

