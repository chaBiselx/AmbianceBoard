
import UpdateVolumeElement from '@/modules/UpdateVolumeElement';
import { MusicElement } from '@/modules/MusicElement';
import Cookie from '@/modules/General/Cookie';
import SharedSoundBoardWebSocket from '@/modules/SharedSoundBoardWebSocket'

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

class MixerElement {
    private readonly DOMMixerElement: HTMLInputElement | null = null;

    constructor(typeMixer: string) {
        const domElementMixer = document.querySelector(`.mixer-playlist[data-type="${typeMixer}"]`);
        if (domElementMixer) {
            this.DOMMixerElement = domElementMixer as HTMLInputElement
        }
    }

    update(value: number): void {
        if(!this.DOMMixerElement) return
        this.DOMMixerElement.value = value.toString();
        this.DOMMixerElement.dispatchEvent(new Event('change'));
    }
}

class MixerManager {
    private readonly listMixer: HTMLCollectionOf<Element>;
    private readonly sharedSoundBoardWebSocket: SharedSoundBoardWebSocket | null = null

    constructor() {
        this.listMixer = document.getElementsByClassName('mixer-playlist');

        const WebSocketUrl = Cookie.get('WebSocketUrl');
        if (WebSocketUrl) {
            this.sharedSoundBoardWebSocket = (SharedSoundBoardWebSocket.getInstance(atob(WebSocketUrl), true));
            this.sharedSoundBoardWebSocket.start();
        }
    }

    public initializeEventListeners(): void {
        for (let mixer of this.listMixer) {
            mixer.addEventListener('change', this.eventChangeVolume.bind(this));
        }
    }

    private eventChangeVolume(event: Event): void {
        const mixer = new MixerBuilder(event.target as HTMLInputElement).getMixer();
        if (mixer.id === 'mixer-general') {
            this.sharedSoundBoardWebSocket?.sendMessage({ type: 'send_mixer_update', data: { type: 'General', value: MixerManager.getMixerValue('general') } });
            const listType = document.getElementsByClassName('mixer-playlist-type');
            for (let typeMixer of listType) {
                const m = new MixerBuilder(typeMixer as HTMLInputElement).getMixer();
                this.changeSpecifiqueVolume(m.type);
            }
        } else {
            this.sharedSoundBoardWebSocket?.sendMessage({ type: 'send_mixer_update', data: { type: mixer.type, value: MixerManager.getMixerValue(mixer.type) } });
            this.changeSpecifiqueVolume(mixer.type);
        }
    }

    private changeSpecifiqueVolume(type: string): void {
        const listAudio = document.getElementsByClassName('audio-' + type);
        for (let audio of listAudio) {

            const musicElement = new MusicElement(audio as HTMLAudioElement);
            new UpdateVolumeElement(musicElement).clearCache(type).update();
        }
    }

    static getMixerValue(type: string): number {
        let input = document.getElementById(`mixer-${type}`) as HTMLInputElement;
        if (input) return parseFloat(input.value);
        return 1;
    }
}


export { MixerManager, MixerElement };