
import UpdateVolumeElement from '@/modules/UpdateVolumeElement';
import { MusicElementFactory } from '@/modules/MusicElementFactory';
import SharedSoundBoardWebSocket from '@/modules/SharedSoundBoardWebSocket'
import SharedSoundBoardUtil from '@/modules/SharedSoundBoardUtil'
export { MixerElement } from '@/modules/MixerElement';

class MixerManager {
    static readonly EventTrigger: string = 'input';
    private static readonly initializedMixers = new WeakSet<HTMLInputElement>();
    private static readonly mixerChangeHandler: EventListener = (event) => {
        MixerManager.eventChangeVolume(event);
    };

    public initializeEventListeners(): void {
        for (const mixer of document.querySelectorAll('.mixer-playlist')) {
            if (!(mixer instanceof HTMLInputElement)) continue;
            if (MixerManager.initializedMixers.has(mixer)) continue;
            mixer.addEventListener(MixerManager.EventTrigger, MixerManager.mixerChangeHandler);
            MixerManager.initializedMixers.add(mixer);
        }
    }

    private static eventChangeVolume(event: Event): void {
        if (!(event.target instanceof HTMLInputElement)) return;

        const mixer = event.target;
        if (mixer.id === 'mixer-general') {
            this.sendMixerUpdate('General', 'general');
            for (const typeMixer of document.querySelectorAll('.mixer-playlist-type[data-type]')) {
                if (!(typeMixer instanceof HTMLInputElement)) continue;
                const type = typeMixer.dataset.type;
                if (type) this.changeSpecificVolume(type);
            }
        } else {
            const type = mixer.dataset.type;
            if (!type) return;
            this.sendMixerUpdate(type, type);
            this.changeSpecificVolume(type);
        }
    }

    private static sendMixerUpdate(type: string, mixerValueType: string): void {
        if (SharedSoundBoardUtil.isSlavePage()) return;
        SharedSoundBoardWebSocket.getMasterInstance().sendMessage({
            type: 'send_mixer_update',
            data: { type, value: this.getMixerValue(mixerValueType) },
        });
    }

    private static changeSpecificVolume(type: string): void {
        for (const audio of document.querySelectorAll<HTMLAudioElement>(`.audio-${type}`)) {
            const musicElement = MusicElementFactory.fromAudioElement(audio);
            new UpdateVolumeElement(musicElement).clearCache(type).update();
        }
    }

    static getMixerValue(type: string): number {
        const input = document.getElementById(`mixer-${type}`);
        if (input instanceof HTMLInputElement) return Number.parseFloat(input.value);
        return 1;
    }
}


export { MixerManager };