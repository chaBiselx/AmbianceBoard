import * as Model from '@/modules/FadeStartegy';
import UpdateVolumeElement from '@/modules/UpdateVolumeElement';
import {MusicElement} from "@/modules/MusicElement";


class AudioFadeManager {
    musicElement: MusicElement;
    audioElement: HTMLAudioElement;
    fadeStrategy: Model.FadeStrategyInterface;
    isFadeIn: boolean;
    onComplete: null|Function;
    duration: number;
    interval: number;
    startVolume: number;    
    endVolume: number;
    updateVolumeElement: UpdateVolumeElement;

    constructor(MusicElement:MusicElement, fadeStrategy = new Model.default.LinearFade(), isFadeIn = true, onComplete:null|Function = null) {
        this.musicElement = MusicElement;
        this.audioElement = MusicElement.DOMElement;
        this.fadeStrategy = fadeStrategy;
        this.isFadeIn = isFadeIn;
        this.onComplete = onComplete;
        this.duration = 1000; // Durée par défaut de 1 seconde
        this.interval = 100; // Intervalle de mise à jour en millisecondes

        this.startVolume = this.isFadeIn ? 0 : 1;
        this.endVolume = this.isFadeIn ? 1 : 0;

        this.musicElement.levelFade  = this.startVolume;
        this.updateVolumeElement = new UpdateVolumeElement(this.musicElement);
        this.updateVolumeElement.update();
    }

    setDuration(durationInSec:number) {
        this.duration = durationInSec * 1000;
    }

    setFadeStrategy(fadeStrategy:Model.FadeStrategyInterface) {
        this.fadeStrategy = fadeStrategy;
    }

    start() {
        let currentTime = 0;
        const intervalId = setInterval(() => {
            currentTime += this.interval;
            const progress = currentTime / this.duration;


            const volume = this.fadeStrategy.calculateVolume(this.startVolume, this.endVolume, progress);
            this.musicElement.levelFade = volume;

            if (currentTime >= this.duration) {
                this.musicElement.levelFade = this.endVolume;
                clearInterval(intervalId);
                if (this.onComplete) {
                    this.onComplete();
                }
            }
            this.updateVolumeElement.update();
        }, this.interval);
    }
}

export default AudioFadeManager;