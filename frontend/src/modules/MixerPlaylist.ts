
import type { uri } from '@/type/General';
import { UpdateVolumePlaylist } from '@/modules/UpdateVolumePlaylist';
import { ButtonPlaylist, ButtonPlaylistFinder } from '@/modules/ButtonPlaylist';


import Cookie from './General/Cookie';
import SharedSoundBoardWebSocket from '@/modules/SharedSoundBoardWebSocket'



class MixerPlaylist {
    private readonly classEvent: string = 'mixer-playlist-update'
    private urlWebSocket : string | null = null;
    private sharedSoundBoardWebSocket: SharedSoundBoardWebSocket | null = null

    constructor() {
        this.urlWebSocket = this.getWebSocketUrl();
        if (this.urlWebSocket) {
            this.startWebSocket();
        }
    }

    private getWebSocketUrl(): string | null {
        return Cookie.get('WebSocketUrl');
    }

    private startWebSocket(): void {
        if (this.urlWebSocket) {
            this.sharedSoundBoardWebSocket = (SharedSoundBoardWebSocket.getMasterInstance());
            this.sharedSoundBoardWebSocket.start();
        }
    }

    public addEventListener() {
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
        if(actualWebSocket != null && actualWebSocket != this.urlWebSocket){
            this.urlWebSocket = actualWebSocket;
            this.startWebSocket();
        }
        if (event.target instanceof HTMLInputElement) {
            if (event.target.dataset.idplaylist) {
                const buttonPlaylist = ButtonPlaylistFinder.search(event.target.dataset.idplaylist)
                if (buttonPlaylist) {
                    const uri = event.target.dataset.playlistupdatevolumeuri as uri;
                    this.updateLocalVolume(buttonPlaylist, parseFloat(event.target.value), uri)
                    this.updateWsVolume(buttonPlaylist, parseFloat(event.target.value))
                }
            }
        }
    }

    private updateLocalVolume(buttonPlaylist: ButtonPlaylist, volume: number, uri: uri) {

        let eventUpdateVolumePlaylist = new UpdateVolumePlaylist(buttonPlaylist, volume);
        eventUpdateVolumePlaylist.updateVolume();
        eventUpdateVolumePlaylist.updateBackend(uri);

    }

    private updateWsVolume(buttonPlaylist: ButtonPlaylist, volume: number) {
        this.sharedSoundBoardWebSocket?.sendMessage({ type: 'send_playlist_update_volume', data: { playlist_uuid: buttonPlaylist.getIdPlaylist(), volume: volume } });
    }


}



export { MixerPlaylist };