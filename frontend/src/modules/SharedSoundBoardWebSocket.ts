import Config from '@/modules/General/Config';
import Cookie from '@/modules/General/Cookie';
import { ButtonPlaylistFinder } from '@/modules/ButtonPlaylist';
import { MusicElement } from '@/modules/MusicElement';
import UpdateVolumeElement from '@/modules/UpdateVolumeElement';
import { SoundBoardManager } from '@/modules/SoundBoardManager';
import { MixerElement } from "@/modules/MixerManager";
import { UpdateVolumePlaylist } from '@/modules/UpdateVolumePlaylist';
import ConsoleCustom from '@/modules/General/ConsoleCustom';
import ConsoleTesteur from '@/modules/General/ConsoleTesteur';

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
type DataVolumePlayOnMaster = {
    'playlist_uuid': string
}

class SharedSoundBoardWebSocket {
    private static instance: SharedSoundBoardWebSocket | null = null;
    private readonly url: string;
    private readonly master: boolean;
    private socket: WebSocket | null = null;

    private constructor(url: string, master: boolean = false) {
        this.url = url;
        this.master = master;
        ConsoleTesteur.log(`WebSocket instance created. Master: ${this.master}`);
    }

    public static setNewInstance(url: string, master: boolean = false): void {
        if (SharedSoundBoardWebSocket.instance) {
            SharedSoundBoardWebSocket.instance.close();
        }
        ConsoleTesteur.log(`WebSocket listen : ${url}`);
        SharedSoundBoardWebSocket.instance = new SharedSoundBoardWebSocket(url, master);
    }

    public static getSlaveInstance(url: string): SharedSoundBoardWebSocket {
        ConsoleTesteur.log(`WebSocket listen : ${url}`);
        SharedSoundBoardWebSocket.instance ??= new SharedSoundBoardWebSocket(url, false);
        return SharedSoundBoardWebSocket.instance;
    }

    public static getMasterInstance(): SharedSoundBoardWebSocket {
        if (!SharedSoundBoardWebSocket.instance) {
            const urlBase64 = Cookie.get('WebSocketUrl');
            if (!urlBase64) {
                throw new Error('URL is required for first instantiation');
            }
            const url = atob(urlBase64);
            SharedSoundBoardWebSocket.instance = new SharedSoundBoardWebSocket(url, true);
            SharedSoundBoardWebSocket.instance.start();
        }
        ConsoleTesteur.log(`WebSocket listen : ${SharedSoundBoardWebSocket.instance.url}`);
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
            ConsoleCustom.log('WebSocket is already connected.');
            return;
        }

        try {
            this.socket = new WebSocket(this.url);

            this.socket.onopen = (_event) => {
                ConsoleCustom.log('WebSocket is connected.');
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
                ConsoleCustom.log('WebSocket Error:', error);
            };
        } catch (error) {
            console.error('Error during WebSocket initialization:', error);
        }

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
            ConsoleCustom.error('WebSocket is not connected. Cannot send message.');
            return false;
        }

        try {
            const jsonString = JSON.stringify(data);
            this.socket.send(jsonString);
            ConsoleCustom.log('Message envoyé:', data);
            return true;
        } catch (error) {
            ConsoleCustom.error('Erreur lors de l\'envoi du message:', error);
            return false;
        }
    }


    private responseProcessing(response: WebSocketResponse): void {
        ConsoleCustom.log('Message reçu:', response);
        ConsoleTesteur.log(`WebSocket response : ${JSON.stringify(response)}`);
        ConsoleCustom.log('master', this.master);
        if (this.master) {
            this.masterProcessing(response);
        } else {
            this.slaveProcessing(response);
        }

    }

    private masterProcessing(response: WebSocketResponse): void {
        switch (response.type) {
            case 'player_play_on_master':
                this.playerPlayOnMaster(response.data as DataVolumePlayOnMaster);
                ConsoleCustom.log('▶️ Démarrage musique de la part d\'un joueur:', response);
                ConsoleTesteur.log(`player_play_on_master from player`);
                return;
        }
    }

    private slaveProcessing(response: WebSocketResponse): void {
        switch (response.type) {
            case 'music_start':
                ConsoleCustom.log('▶️ Démarrage musique:', response);
                ConsoleTesteur.log(`music_start`);
                this.startMusic(response.data as DataMusic);
                return;
            case 'music_stop':
                this.stopMusic(response.data as DataMusic);
                ConsoleTesteur.log(`music_stop`);
                ConsoleCustom.log('⏹️ Arrêt musique:', response);
                return;
            case 'music_stop_all':
                this.stopAll();
                ConsoleTesteur.log(`music_stop_all`);
                ConsoleCustom.log('⏹️ Arrêt toutes musiques:', response);
                return;
            case 'mixer_update':
                this.updateMixer(response.data as DataMixer);
                ConsoleCustom.log('🔄 update mixer:', response);
                ConsoleTesteur.log(`mixer_update`);
                return;
            case 'playlist_update_volume':
                this.updateVolumePlaylist(response.data as DataVolumePlaylist);
                ConsoleCustom.log('🔄 update volume playlist:', response);
                ConsoleTesteur.log(`playlist_update_volume`);
                return;
            default:
                ConsoleCustom.error('❌ Erreur:', response);
                ConsoleTesteur.log(`Unknown response type: ${response.type}`);
                return;

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

    private playerPlayOnMaster(data: DataVolumePlayOnMaster): void {
        console.group('playerPlayOnMaster');
        if (!data.playlist_uuid) return;
        const buttonPlaylist = ButtonPlaylistFinder.search(data.playlist_uuid);
        if (!buttonPlaylist) return;
        buttonPlaylist.active();
        SoundBoardManager.addPlaylist(buttonPlaylist);
        console.groupEnd();
    }
}

export default SharedSoundBoardWebSocket;