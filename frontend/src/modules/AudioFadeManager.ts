import * as Model from '@/modules/FadeStartegy';
import UpdateVolumeElement from '@/modules/UpdateVolumeElement';
import { MusicElement } from "@/modules/MusicElement";


class AudioFadeManager {
    musicElement: MusicElement;
    audioElement: HTMLAudioElement;
    fadeStrategy: Model.FadeStrategyInterface;
    isFadeIn: boolean;
    onComplete: null | Function;
    duration: number;
    interval: number;
    startVolume: number;
    endVolume: number;
    updateVolumeElement: UpdateVolumeElement;

    constructor(MusicElement: MusicElement, fadeStrategy = new Model.default.LinearFade(), isFadeIn = true, onComplete: null | Function = null) {
        this.musicElement = MusicElement;
        this.audioElement = MusicElement.DOMElement;
        this.fadeStrategy = fadeStrategy;
        this.isFadeIn = isFadeIn;
        this.onComplete = onComplete;
        this.duration = 1000; // Durée par défaut de 1 seconde
        this.interval = 200; // Intervalle de mise à jour en millisecondes

        this.startVolume = this.isFadeIn ? 0 : 1;
        this.endVolume = this.isFadeIn ? 1 : 0;

        this.musicElement.levelFade = this.startVolume;
        this.updateVolumeElement = new UpdateVolumeElement(this.musicElement);
        this.updateVolumeElement.update();

    }

    public setDuration(durationInSec: number) {
        this.duration = durationInSec * 1000;
    }

    public setFadeStrategy(fadeStrategy: Model.FadeStrategyInterface) {
        this.fadeStrategy = fadeStrategy;
    }

    public start() {
        const startTime = Date.now();
        let lastLevelFade = this.musicElement.levelFade;

        const intervalId = setInterval(() => {
            const elapsed = Date.now() - startTime;
            const progress = Math.min(1, elapsed / this.duration);

            const volume = this.fadeStrategy.calculateVolume(
                this.startVolume,
                this.endVolume,
                progress
            );

            if (volume < 1 && volume >= lastLevelFade + 0.05 ) { // mise à jour seulement si le volume a changé de 0.05 ou plus
                this.musicElement.levelFade = volume;
                this.updateVolumeElement.update();
                lastLevelFade = this.musicElement.levelFade;
            }

            if (progress >= 1) {
                clearInterval(intervalId);
                this.musicElement.levelFade = this.endVolume;
                this.updateVolumeElement.update(); // dernière mise à jour finale
                this.onComplete?.();
            }
        }, this.interval);
    }
}

export default AudioFadeManager;