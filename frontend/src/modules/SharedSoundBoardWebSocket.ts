import Config from '@/modules/Config';
import { ButtonPlaylistFinder } from '@/modules/ButtonPlaylist';
import { MusicElement } from '@/modules/MusicElement';
import UpdateVolumeElement from '@/modules/UpdateVolumeElement';
import { SoundBoardManager } from '@/modules/SoundBoardManager';
import { MixerElement } from "@/modules/MixerManager";
import { UpdateVolumePlaylist } from '@/modules/UpdateVolumePlaylist';

type DataMusic = {
    'track': number | null
    'playlist_uuid': string,
    'url_music': string | null
}
type DataMixer = {
    'typeMixer': string
    'value': number
}
type DataVolumePlaylist = {
    'playlist_uuid': string
    'volume': number
}
type WebSocketResponse = {
    'type': string
    'data': DataMusic | DataMixer | DataVolumePlaylist
}

class SharedSoundBoardWebSocket {
    private static instance: SharedSoundBoardWebSocket | null = null;
    private readonly url: string;
    private readonly master: boolean;
    private socket: WebSocket | null = null;

    private constructor(url: string, master: boolean = false) {
        this.url = url;
        this.master = master;
    }

    public static getInstance(url?: string, master: boolean = false): SharedSoundBoardWebSocket {
        if (!SharedSoundBoardWebSocket.instance) {
            if (!url) {
                throw new Error('URL is required for first instantiation');
            }
            SharedSoundBoardWebSocket.instance = new SharedSoundBoardWebSocket(url, master);
        }
        return SharedSoundBoardWebSocket.instance;
    }

    public static resetInstance(): void {
        if (SharedSoundBoardWebSocket.instance?.socket) {
            SharedSoundBoardWebSocket.instance.socket.close();
        }
        SharedSoundBoardWebSocket.instance = null;
    }

    public start(): void {
        // Éviter de créer plusieurs connexions WebSocket
        if (this.socket && this.socket.readyState === WebSocket.OPEN) {
            if (Config.DEBUG) console.log('WebSocket is already connected.');
            return;
        }

        this.socket = new WebSocket(this.url);

        this.socket.onopen = (event) => {
            if (Config.DEBUG) console.log('WebSocket is connected.');
        };

        this.socket.onmessage = (event) => {
            this.responseProcessing(JSON.parse(event.data) as WebSocketResponse);
        };

        this.socket.onclose = (event) => {
            if (Config.DEBUG) {
                if (event.wasClean) {
                    console.log(`Connection closed cleanly, code=${event.code}, reason=${event.reason}`);
                } else {
                    console.log('Connection died');
                }
            }

            this.socket = null;
        };

        this.socket.onerror = (error) => {
            if (Config.DEBUG) console.log('WebSocket Error:', error);
        };
    }

    public close(): void {
        if (this.socket) {
            this.socket.close();
            this.socket = null;
        }
    }

    public getConnectionState(): number | null {
        return this.socket?.readyState ?? null;
    }

    public sendMessage(data: object): boolean {
        if (!this.socket || this.socket.readyState !== WebSocket.OPEN) {
            if (Config.DEBUG) console.error('WebSocket is not connected. Cannot send message.');
            return false;
        }

        try {
            const jsonString = JSON.stringify(data);
            this.socket.send(jsonString);
            if (Config.DEBUG) console.log('Message envoyé:', data);
            return true;
        } catch (error) {
            if (Config.DEBUG) console.error('Erreur lors de l\'envoi du message:', error);
            return false;
        }
    }

    private responseProcessing(response: WebSocketResponse): void {
        if (this.master) return
        if (Config.DEBUG) console.log('Message reçu:', response);
        if (Config.DEBUG) console.log('master', this.master);
        switch (response.type) {
            case 'music_start':
                if (Config.DEBUG) console.log('▶️ Démarrage musique:', response);
                this.startMusic(response.data as DataMusic);
                break;
            case 'music_stop':
                this.stopMusic(response.data as DataMusic);
                if (Config.DEBUG) console.log('⏹️ Arrêt musique:', response);
                break;
            case 'music_stop_all':
                this.stopAll();
                if (Config.DEBUG) console.log('⏹️ Arrêt toutes musiques:', response);
                break;
            case 'mixer_update':
                this.updateMixer(response.data as DataMixer);
                if (Config.DEBUG) console.log('🔄 update mixer:', response);
                break;
            case 'playlist_update_volume':
                this.updateVolumePlaylist(response.data as DataVolumePlaylist);
                if (Config.DEBUG) console.log('🔄 update volume playlist:', response);
                break;
            default:
                if (Config.DEBUG) console.error('❌ Erreur:', response);
                break;
        }
    }

    private startMusic(data: DataMusic): void {
        if (!data.url_music) return;

        const buttonPlaylist = ButtonPlaylistFinder.search(data.playlist_uuid);
        if (!buttonPlaylist) return;

        const musicElement = new MusicElement(buttonPlaylist);
        (new UpdateVolumeElement(musicElement)).update();
        musicElement.addToDOM();
        musicElement.setSpecificMusic(data.url_music);
        musicElement.play();
    }

    private stopMusic(data: DataMusic): void {
        const buttonPlaylist = ButtonPlaylistFinder.search(data.playlist_uuid);
        if (!buttonPlaylist) return;
        SoundBoardManager.removePlaylist(buttonPlaylist);
    }

    private stopAll(): void {
        SoundBoardManager.deleteAllMusicPlaylist();
    }

    private updateMixer(data: DataMixer): void {
        new MixerElement(data.typeMixer).update(data.value);
    }

    private updateVolumePlaylist(data: DataVolumePlaylist): void {
        const buttonPlaylist = ButtonPlaylistFinder.search(data.playlist_uuid);
        if (!buttonPlaylist) return;
        let eventUpdateVolumePlaylist = new UpdateVolumePlaylist(buttonPlaylist, data.volume);
        eventUpdateVolumePlaylist.updateVolume();
    }
}

export default SharedSoundBoardWebSocket;