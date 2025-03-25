
import UpdateVolumeElement from '@/modules/UpdateVolumeElement';
import { MusicElement } from './MusicElement';

type mixer = {
    id: string,
    type: string
    input: HTMLInputElement
}

class MixerBuilder {
    private readonly mixer: mixer;

    constructor(input: HTMLInputElement) {
        this.mixer = {
            input: input,
            type: input.dataset.type!,
            id: input.id
        }
    }

    getMixer(): mixer {
        return this.mixer;
    }
}

class MixerManager{
    private readonly listMixer: HTMLCollectionOf<Element>;

    constructor() {
        this.listMixer = document.getElementsByClassName('mixer-playlist');
    }

    public initializeEventListeners(): void {
        for (let mixer of this.listMixer) {
            mixer.addEventListener('change', this.eventChangeVolume.bind(this));
        }
    }

    private eventChangeVolume(event: Event): void {
        const mixer = new MixerBuilder(event.target as HTMLInputElement).getMixer();
        if (mixer.id === 'mixer-general') {
            const listType = document.getElementsByClassName('mixer-playlist-type');
            for (let typeMixer of listType) {
                const m = new MixerBuilder(typeMixer as HTMLInputElement).getMixer();
                this.changeSpecifiqueVolume(m.type);
            }
        } else {
            this.changeSpecifiqueVolume(mixer.type);
        }
    }

    private changeSpecifiqueVolume(type: string): void {
        const listAudio = document.getElementsByClassName('audio-' + type);
        for (let audio of listAudio) {

            const musicElement = new MusicElement(audio as HTMLAudioElement);
            
            new UpdateVolumeElement(musicElement).update();
        }
    }

    static getMixerValue(type: string): number {
        let input = document.getElementById(`mixer-${type}`) as HTMLInputElement;
        if (input) return parseFloat(input.value);
        return 1;
    }
}


export {MixerManager};