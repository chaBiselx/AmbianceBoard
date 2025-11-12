
import type { uri } from '@/type/General';
import { UpdateVolumePlaylist } from '@/modules/UpdateVolumePlaylist';
import { ButtonPlaylist, ButtonPlaylistFinder, ListingButtonPlaylist } from '@/modules/ButtonPlaylist';


import Cookie from './General/Cookie';
import SharedSoundBoardWebSocket from '@/modules/SharedSoundBoardWebSocket'
import SharedSoundBoardUtil from '@/modules/SharedSoundBoardUtil'
import ConsoleTesteur from '@/modules/General/ConsoleTesteur';


class MixerPlaylist {
    private readonly classEvent: string = 'mixer-playlist-update'
    private urlWebSocket: string | null = null;
    private sharedSoundBoardWebSocket: SharedSoundBoardWebSocket | null = null
    private idCheckBoxToggle: string = 'inputShowMixerPlaylist'
    private idContainerPlaylistMixer: string = 'mixer-playlist-update-container'
    private idSaveBackendValue: string = 'saveVolumePlaylistMixer'

    constructor() {
        this.urlWebSocket = this.getWebSocketUrl();
        if (this.urlWebSocket) {
            this.startWebSocket();
        }
    }

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
        const switchInput = document.getElementById(this.idSaveBackendValue) as HTMLInputElement
        switchInput.checked = false;
    }

    private getWebSocketUrl(): string | null {
        return Cookie.get('WebSocketUrl');
    }

    private startWebSocket(): void {
        if (this.urlWebSocket && !SharedSoundBoardUtil.isSlavePage()) {
            ConsoleTesteur.log("WebSocket Master call from MixerPlaylist.startWebSocket");

            this.sharedSoundBoardWebSocket = (SharedSoundBoardWebSocket.getMasterInstance());
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
        const actualWebSocket = this.getWebSocketUrl()
        if (actualWebSocket != null && actualWebSocket != this.urlWebSocket) {
            this.urlWebSocket = actualWebSocket;
            this.startWebSocket();
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