
import type { uri } from '@/type/General';
import { UpdateVolumePlaylist } from '@/modules/UpdateVolumePlaylist';
import { ButtonPlaylist, ButtonPlaylistFinder } from '@/modules/ButtonPlaylist';


import Cookie from './General/Cookie';
import SharedSoundBoardWebSocket from '@/modules/SharedSoundBoardWebSocket'



class MixerPlaylist {
    private readonly sharedSoundBoardWebSocket: SharedSoundBoardWebSocket | null = null;
    private readonly classEvent: string = 'mixer-playlist-update'

    constructor() {
        const WebSocketUrl = Cookie.get('WebSocketUrl');
        if (WebSocketUrl) {
            this.sharedSoundBoardWebSocket = (SharedSoundBoardWebSocket.getInstance(atob(WebSocketUrl), true));
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