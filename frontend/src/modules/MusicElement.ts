import Config from '../modules/Config';
import Notification from '../modules/Notifications';

import { ButtonPlaylist, ButtonPlaylistFinder } from '../modules/ButtonPlaylist';
import * as Model from '../modules/FadeStartegy';
import AudioFadeManager from '../modules/AudioFadeManager';
import { SoundBoardManager } from '../modules/SoundBoardManager';

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


    constructor(Element: HTMLAudioElement | ButtonPlaylist) {
        if (Element instanceof HTMLAudioElement) {
            this.DOMElement = Element;
            this.setDefaultValue();
        } else {
            this.DOMElement = document.createElement('audio');
            this.setDefaultFromPlaylist(Element);
        }

    }

    private setDefaultValue() {
        if (this.DOMElement.dataset.defaultvolume) {
            this.defaultVolume = parseFloat(this.DOMElement.dataset.defaultvolume);
        }
        if (this.DOMElement.dataset.fadein) {
            this.fadeIn = (this.DOMElement.dataset.fadein == "true" ? true : false);
        }
        if (this.DOMElement.dataset.fadeintype) {
            this.fadeInType = this.DOMElement.dataset.fadeintype;
        }
        if (this.DOMElement.dataset.fadeinduration) {
            this.fadeInDuration = parseFloat(this.DOMElement.dataset.fadeinduration);
        }
        if (this.DOMElement.dataset.fadeout) {
            this.fadeOut = (this.DOMElement.dataset.fadeout == "true" ? true : false);
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
            this.playlistLoop = (this.DOMElement.dataset.playlistloop == "true" ? true : false);
        }
    }

    private setDefaultFromPlaylist(buttonPlaylist: ButtonPlaylist): void {
        if (buttonPlaylist.dataset.playlistVolume) {
            this.setDefaultVolume(buttonPlaylist.getVolume());
        }
        if (buttonPlaylist.dataset.playlistFadein) {
            this.fadeIn = (buttonPlaylist.dataset.playlistFadein == TRUE) ? true : false;
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
        if (buttonPlaylist.dataset.playlistFadeout) {
            this.fadeOut = (buttonPlaylist.dataset.playlistFadein == TRUE) ? true : false;
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
        if (buttonPlaylist.dataset.playlistType) {
            this.playlistType = buttonPlaylist.dataset.playlistType
            this.DOMElement.dataset.playlisttype = this.playlistType;
        }
        if (buttonPlaylist.idPlaylist) {
            this.idPlaylist = buttonPlaylist.idPlaylist;
            this.DOMElement.dataset.playlistid = this.idPlaylist;
        }
        if (buttonPlaylist.dataset.playlistLoop) {
            this.playlistLoop = (buttonPlaylist.dataset.playlistLoop == TRUE) ? true : false;
            this.DOMElement.dataset.playlistloop = this.playlistLoop.toString();
        }



        this.DOMElement.className = `playlist-audio-${buttonPlaylist.idPlaylist}`;

        this.DOMElement.classList.add('audio-' + buttonPlaylist.dataset.playlistType)
        this.DOMElement.src = buttonPlaylist.dataset.playlistUri + "?i=" + Date.now();
        this.DOMElement.controls = (Config.DEBUG) ? true : false;
        this.DOMElement.autoplay = true;
    }

    public setDefaultVolume(volume: number) {
        this.defaultVolume = volume;
        this.DOMElement.dataset.defaultvolume = this.defaultVolume.toString();
    }

    public addToDOM(): MusicElement {
        const audioElementDiv = document.getElementById(Config.SOUNDBOARD_DIV_ID_PLAYERS) as HTMLElement;
        audioElementDiv.appendChild(this.DOMElement);
        return this
    }

    public delete() {
        const buttonPlaylist = ButtonPlaylistFinder.search(this.idPlaylist) as ButtonPlaylist;
        buttonPlaylist.disactive();
        this.DOMElement.remove();
    }



    public play() {
        this.DOMElement.addEventListener('error', function (event: Event) {
            if (event.target && event.target instanceof HTMLAudioElement) {
                if (event.target.error && event.target.error.code === 4) { // => ERROR 404
                    let new_music = new MusicElement(event.target);

                    const buttonPlaylist = ButtonPlaylistFinder.search(new_music.idPlaylist as string) as ButtonPlaylist;
                    buttonPlaylist.disactive();
                    Notification.createClientNotification({ message: 'Aucune musique n\'est presente dans cette playlist', type: 'danger', duration: 2000 });
                    event.target.remove();
                }
            }
        });
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

    public addFadeIn() {
        if (Config.DEBUG) console.log('addFadeIn');
        this.levelFade = 0;
        this.DOMElement.dataset.fadeInGoing = true.toString();

        let typeFade = Model.default.FadeSelector.selectTypeFade(this.fadeInType)
        let audioFade = new AudioFadeManager(this, typeFade, true, () => {
            this.levelFade = 1;
            delete this.DOMElement.dataset.fadeInGoing;
        });
        audioFade.setDuration(this.fadeInDuration);

        this.DOMElement.addEventListener('playing', () => {
            let time = Date.now();
            while (this.DOMElement.readyState != 2) {
                if (time + 50 < Date.now()) {
                    break;
                }
            }
            audioFade.start();
        })

    }

    public addFadeOut() {
        if (Config.DEBUG) console.log('addFadeOut');
        if (this.DOMElement.dataset.fadeInGoing) {
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

        if (timeRemaining <= new_music.fadeOutDuration && new_music.fadeOut == true) {
            const buttonPlaylist = ButtonPlaylistFinder.search(new_music.idPlaylist);
            if (buttonPlaylist) {


                new_music.DOMElement.removeEventListener('timeupdate', new_music.eventFadeOut);
                new_music.addFadeOut();
                if (new_music.playlistLoop) {
                    if (Config.DEBUG) console.log("eventFadeOut loop");
                    SoundBoardManager.createPlaylistLink(buttonPlaylist);
                } else {
                    buttonPlaylist.disactive();
                }
            }
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
        if (new_music.playlistLoop) {
            const buttonPlaylist = ButtonPlaylistFinder.search(new_music.idPlaylist) as ButtonPlaylist;
            SoundBoardManager.addPlaylist(buttonPlaylist);
        } else {
            const buttonPlaylist = ButtonPlaylistFinder.search(new_music.idPlaylist) as ButtonPlaylist;
            buttonPlaylist.disactive();
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
}

export { MusicElement, ListingAudioElement, SearchMusicElement };

