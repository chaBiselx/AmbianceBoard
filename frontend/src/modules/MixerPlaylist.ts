
import type { uri } from '@/type/General';
import { UpdateVolumePlaylist } from '@/modules/UpdateVolumePlaylist';
import { ButtonPlaylist, ButtonPlaylistFinder } from '@/modules/ButtonPlaylist';
import SharedSoundBoardWebSocket from '@/modules/SharedSoundBoardWebSocket'
import SharedSoundBoardUtil from '@/modules/SharedSoundBoardUtil'


class MixerPlaylist {
    private readonly classEvent: string = 'mixer-playlist-update'
    private readonly idCheckBoxToggle: string = 'inputShowMixerPlaylist'
    private readonly idContainerPlaylistMixer: string = 'mixer-playlist-update-container'
    private readonly idSaveBackendValue: string = 'saveVolumePlaylistMixer'
    private sharedSoundBoardWebSocket: SharedSoundBoardWebSocket | null = null

    private needSaveBackend(): boolean {
        const switchInput = document.getElementById(this.idSaveBackendValue) as HTMLInputElement
        if (switchInput?.checked) {
            return true;
        }
        return false;
    }

    private togglePlaylistMixer() {
        const listMixerUpdate = document.getElementsByClassName(this.idContainerPlaylistMixer);
        const checkBox = document.getElementById(this.idCheckBoxToggle) as HTMLInputElement
        document.getElementById(`${this.idCheckBoxToggle}-show`)?.classList.toggle('d-none')
        document.getElementById(`${this.idCheckBoxToggle}-hide`)?.classList.toggle('d-none')
        document.getElementById(`${this.idSaveBackendValue}-div`)?.classList.toggle('d-none')

        const showMixer = checkBox.checked
        if (listMixerUpdate) {
            for (const mixerUpdate of listMixerUpdate) {
                if (showMixer) {
                    mixerUpdate.classList.remove('hide-playlist-mixer');
                } else {
                    mixerUpdate.classList.add('hide-playlist-mixer');
                    this.resetInputSaveBackendValue();
                }
            }
        }
    }

    private resetInputSaveBackendValue() {
        const switchInput = document.getElementById(this.idSaveBackendValue) as HTMLInputElement|null
        if(switchInput){
            switchInput.checked = false;
        }
    }

    public addEventListener() {
        this.addEventUpdateVolume();
        this.addEventToggle();
    }

    private addEventToggle() {
        const inputShowMixerPlaylist = document.getElementById('inputShowMixerPlaylist');
        if (inputShowMixerPlaylist) {
            inputShowMixerPlaylist.addEventListener('change', this.togglePlaylistMixer.bind(this));
        }
    }

    private addEventUpdateVolume() {
        const listMixerUpdate = document.getElementsByClassName(this.classEvent);
        if (listMixerUpdate) {
            for (const mixerUpdate of listMixerUpdate) {
                mixerUpdate.addEventListener('change', (event: Event) => {
                    this.eventUpdatePlaylistVolume(event)
                });
            }
        }
    }

    private eventUpdatePlaylistVolume(event: Event) {
        // Récupérer l'instance WebSocket si disponible (auto-initialisée au chargement)
        if (!SharedSoundBoardUtil.isSlavePage() && !this.sharedSoundBoardWebSocket) {
            this.sharedSoundBoardWebSocket = SharedSoundBoardWebSocket.getMasterInstance();
        }
        
        if (event.target instanceof HTMLInputElement) {
            if (event.target.dataset.idplaylist) {
                const buttonPlaylist = ButtonPlaylistFinder.search(event.target.dataset.idplaylist)
                if (buttonPlaylist) {
                    const uri = event.target.dataset.playlistupdatevolumeuri as uri;
                    this.updateLocalVolume(buttonPlaylist, Number.parseFloat(event.target.value), uri)
                    this.updateWsVolume(buttonPlaylist, Number.parseFloat(event.target.value))
                }
            }
        }
    }

    private updateLocalVolume(buttonPlaylist: ButtonPlaylist, volume: number, uri: uri) {

        let eventUpdateVolumePlaylist = new UpdateVolumePlaylist(buttonPlaylist);
        eventUpdateVolumePlaylist.updateVolume(volume);
        if (this.needSaveBackend()) {
            eventUpdateVolumePlaylist.updateBackend(uri, volume);
        }

    }

    private updateWsVolume(buttonPlaylist: ButtonPlaylist, volume: number) {
        this.sharedSoundBoardWebSocket?.sendMessage({ type: 'send_playlist_update_volume', data: { playlist_uuid: buttonPlaylist.getIdPlaylist(), volume: volume } });
    }


}



export { MixerPlaylist };