
import type { uri } from '@/type/General';
import { UpdateVolumePlaylist } from '@/modules/UpdateVolumePlaylist';
import { ButtonPlaylist, ButtonPlaylistFinder } from '@/modules/ButtonPlaylist';
import SharedSoundBoardWebSocket from '@/modules/SharedSoundBoardWebSocket'
import SharedSoundBoardUtil from '@/modules/SharedSoundBoardUtil'
import { SoundBoardManager } from '@/modules/SoundBoardManager'
import { MusicElementFactory } from '@/modules/MusicElementFactory'
import UpdateVolumeElement from '@/modules/UpdateVolumeElement'
import Time from './Util/Time';
import ConsoleCustom from '@/modules/General/ConsoleCustom';



class MixerPlaylist {
    private readonly classEvent: string = 'mixer-playlist-update'
    private readonly idCheckBoxToggle: string = 'inputShowMixerPlaylist'
    private readonly idContainerPlaylistMixer: string = 'mixer-playlist-update-container'
    private readonly idSaveBackendValue: string = 'saveVolumePlaylistMixer'
    private readonly inputShowSpecificMusic: string = 'inputShowSpecificMusic'
    private readonly classSpecificMusicContainer: string = 'js-specific-music'
    private readonly classMarginSpecificMusic: string = 'js-margin-specific-music'
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

    private async toggleSpecificMusic() {
        const containers = document.getElementsByClassName(this.classSpecificMusicContainer);
        const checkBox = document.getElementById(this.inputShowSpecificMusic) as HTMLInputElement
        document.getElementById(`${this.inputShowSpecificMusic}-show`)?.classList.toggle('d-none')
        document.getElementById(`${this.inputShowSpecificMusic}-hide`)?.classList.toggle('d-none')

        const showSpecificMusic = checkBox.checked
        if (!containers) return

        if (showSpecificMusic) {
            const tracksData = await this.fetchAllTracks()
            if (tracksData) {
                this.distributeTracksToContainers(containers, tracksData)
            }
            this.toggleSpecificMusicToggle(true)
        } else {
            this.toggleSpecificMusicToggle(false)
        }
    }

    private toggleSpecificMusicToggle(bool: boolean = false) {
        const containers = document.getElementsByClassName(this.classSpecificMusicContainer);
        const marginContainers = document.getElementsByClassName(this.classMarginSpecificMusic);
        for (const container of containers) {
            if (bool) {
                container.classList.remove('d-none')
            } else {
                container.classList.add('d-none');
            }
        }
        console.log(marginContainers);
        
        for (const marginContainer of marginContainers) {
            if (bool) {
                marginContainer.classList.remove('d-none')
            } else {
                marginContainer.classList.add('d-none');
            }
        }
    }

    private async fetchAllTracks(): Promise<Record<string, Array<{ id: number, name: string, duration: number | null, uri: string }>> | null> {
        if (document.querySelectorAll('.specific-music-item').length > 0) {
            return null;
        }

        const mainContainer = document.querySelector('.responsive-sections-container') as HTMLElement | null
        const tracksUri = mainContainer?.dataset.soundboardTracksUri
        if (!tracksUri) return null

        try {
            const response = await fetch(tracksUri)
            if (!response.ok) return null
            return await response.json()
        } catch {
            return null
        }
    }

    private distributeTracksToContainers(containers: HTMLCollectionOf<Element>, tracksData: Record<string, Array<{ id: number, name: string, duration: number | null, uri: string }>>) {
        for (const container of containers) {
            container.classList.remove('d-none')
            const htmlContainer = container as HTMLElement
            const playlistId = htmlContainer.dataset.playlistId
            if (!playlistId) continue

            const listContainer = htmlContainer.querySelector('.specific-music-list')
            if (!listContainer) continue

            const tracks = tracksData[playlistId]
            this.renderTrackList(listContainer, playlistId, tracks)
        }
    }

    private renderTrackList(listContainer: Element, playlistId: string, tracks: Array<{ id: number, name: string, duration: number | null, uri: string }> | undefined) {
        listContainer.innerHTML = ''
        if (!tracks || tracks.length === 0) {
            listContainer.innerHTML = '<div class="specific-music-empty"><small>Aucune piste</small></div>'
            return
        }

        for (const track of tracks) {
            const trackItem = document.createElement('div')
            trackItem.classList.add('specific-music-item', 'cursor-pointer')
            trackItem.dataset.trackId = String(track.id)
            trackItem.dataset.uri = track.uri

            const playIcon = document.createElement('small')
            playIcon.classList.add('specific-music-play')
            playIcon.innerHTML = '<i class="fa-solid fa-play"></i> '

            const trackName = document.createElement('small')
            trackName.classList.add('specific-music-name')
            trackName.textContent = track.name

            const trackDuration = document.createElement('small')
            trackDuration.classList.add('specific-music-duration')
            trackDuration.textContent = track.duration !== null ? Time.formatDuration(track.duration) : ''

            trackItem.appendChild(playIcon)
            trackItem.appendChild(trackName)
            trackItem.appendChild(trackDuration)
            listContainer.appendChild(trackItem)

            trackItem.addEventListener('click', (el) => {
                ConsoleCustom.log("clickTrackItem", { "event": el, "trackId": track.id, "trackUri": track.uri, "playlistId": playlistId });
                this.playSpecificTrack(playlistId, track.uri)
            })
        }
    }

    private playSpecificTrack(playlistId: string, trackUri: string) {
        const buttonPlaylist = ButtonPlaylistFinder.search(playlistId)
        if (!buttonPlaylist) return

        SoundBoardManager.deleteSameTypePlaylist(buttonPlaylist)

        const musicElement = MusicElementFactory.fromButtonPlaylist(buttonPlaylist)
        musicElement.setSpecificMusic(trackUri);
        (new UpdateVolumeElement(musicElement)).update()
        musicElement.addToDOM()
        musicElement.play()
        buttonPlaylist.active()

        // Fermer le toggle des tracks
        this.closeSpecificMusicToggle()
    }

    private closeSpecificMusicToggle() {
        const checkBox = document.getElementById(this.inputShowSpecificMusic) as HTMLInputElement | null
        if (checkBox && checkBox.checked) {
            checkBox.checked = false
            checkBox.dispatchEvent(new Event('change'))
        }
    }

    private resetInputSaveBackendValue() {
        const switchInput = document.getElementById(this.idSaveBackendValue) as HTMLInputElement | null
        if (switchInput) {
            switchInput.checked = false;
        }
    }

    public addEventListener() {
        this.addEventUpdateVolume();
        this.addEventMixerButtonToggle();
        this.addEventSpecificMusicButtonToggle();
    }

    private addEventMixerButtonToggle() {
        const inputShowMixerPlaylist = document.getElementById('inputShowMixerPlaylist');
        if (inputShowMixerPlaylist) {
            inputShowMixerPlaylist.addEventListener('change', this.togglePlaylistMixer.bind(this));
        }
    }

    private addEventSpecificMusicButtonToggle() {
        const inputShowSpecificMusic = document.getElementById('inputShowSpecificMusic');
        if (inputShowSpecificMusic) {
            inputShowSpecificMusic.addEventListener('change', this.toggleSpecificMusic.bind(this));
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