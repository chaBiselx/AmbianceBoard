import PageFocusReloader from "@/modules/General/PageFocusReloader";
import Csrf from '@/modules/General/Csrf';
import ConsoleCustom from "@/modules/General/ConsoleCustom";

document.addEventListener("DOMContentLoaded", () => {
    new PageFocusReloader().setupFocusListener();
    new UpdatePlaylistActionableByPlayers().initEventListeners;
});

type valueType = string | boolean | number;

type UpdatePlaylistConfig = {
    soundboard_uuid: string;
    playlist_uuid: string;
    soundboard_playlist_id: string;
    label: string;
    value: valueType;
}

class UpdatePlaylistActionableByPlayers {
    private readonly playlistsTableBody: HTMLElement;
    private readonly url: string;
    constructor() {
        this.playlistsTableBody = document.getElementById('playlists-table-body') as HTMLElement;
        this.url = this.playlistsTableBody.dataset.updateUrl as string;
    }

    public initEventListeners(): void {
        this.playlistsTableBody.getElementsByClassName('update-action')
        for (const input of this.playlistsTableBody.getElementsByClassName('update-action')) {
            input.addEventListener('change', (event) => this.updateInput(event));
        }
    }

    private updateInput(event: Event): void {
        const target = event.target as HTMLInputElement;
        if (target) {
            const playlistUuid = target.dataset.playlistUuid;
            const soundboard_uuid = target.dataset.soundboardUuid;
            const soundboardPlaylistId = target.dataset.soundboardPlaylistId;
            const label = target.dataset.label;
            if (playlistUuid && soundboardPlaylistId && soundboard_uuid && label) {
                const value = this.valueFromInput(target);
                const param: UpdatePlaylistConfig = {
                    soundboard_uuid: soundboard_uuid,
                    playlist_uuid: playlistUuid,
                    soundboard_playlist_id: soundboardPlaylistId,
                    label: label,
                    value: value
                };
                this.updateValueAction(param);
            }
        }
    }

    private valueFromInput(input: HTMLInputElement): valueType {
        if (input.type === 'checkbox') {
            return input.checked;
        }
        return input.value;
    }

    private updateValueAction(param: UpdatePlaylistConfig) {
        fetch(this.url, {
            method: 'UPDATE',
            headers: {
                'X-CSRFToken': Csrf.getToken()!,
            },
            body: JSON.stringify(param)
        })
            .then(response => {
                if (response.status === 200) {
                    ConsoleCustom.debug('Valeur mise a jour');
                    // Rediriger vers l'URL fournie
                } else {
                    // Gestion des erreurs
                    ConsoleCustom.error('Erreur lors de la mise à jour');
                }
            })
            .catch(error => {
                ConsoleCustom.error('Erreur lors de la requête AJAX:', error);
            });
    }

}
