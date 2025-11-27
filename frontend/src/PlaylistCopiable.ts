import { PlayerCustomFactory } from '@/modules/Audio/PlayerCustom';
import Notification from '@/modules/General/Notifications';
import Csrf from "@/modules/General/Csrf";

document.addEventListener('DOMContentLoaded', () => {
    const listButtons = document.querySelectorAll('.playlist-copiable');
    const previewPlaylistDiv = document.getElementById('preview-playlist-div')
    if (previewPlaylistDiv) {
        const playlistPreviewer = new PlaylistCopiable(previewPlaylistDiv.dataset.urlPreview!);
        for (const buttons of listButtons) {
            buttons.addEventListener('click', (event) => {
                const target = event.target as HTMLElement;
                playlistPreviewer.getPreview(target.dataset.playlistUuid!);
            });
        }
    }

});

class PlaylistCopiable {
    private readonly urlPreview: string;
    private urlDuplication: string | null = null;

    constructor(urlPreview: string) {
        this.urlPreview = urlPreview;
    }

    public getPreview(playlistUuid: string) {
        fetch(`${this.urlPreview}?playlistUuid=${playlistUuid}`)
            .then(response => response.text())
            .then(data => {
                const previewDiv = document.getElementById('previewPlaylist');
                if (previewDiv) {
                    previewDiv.innerHTML = data;
                    PlayerCustomFactory.create();
                    this.addEventDuplicateButton();
                }
            })
            .catch(error => {
                console.error('Error fetching playlist preview:', error);
            });
    }

    private addEventDuplicateButton() {
        const duplicateButton = document.getElementById('duplicate-playlist-button');
        this.urlDuplication = duplicateButton?.dataset.urlDuplication || null;
        if (duplicateButton) {
            duplicateButton.addEventListener('click', this.duplicatePreview.bind(this));
        }
    }

    private duplicatePreview() {
        document.getElementById('duplicate-playlist-button')?.setAttribute('disabled', 'true');
        fetch(`${this.urlDuplication}`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': Csrf.getToken()!,
            },
        })
            .then(async response => {
                const data = await response.json();
                return { data, status: response.status, ok: response.ok };
            })
            .then(({ data, status, ok }) => {
                if (ok && data.success) {
                    Notification.createClientNotification({ 
                        message: data.message || 'Playlist dupliquée avec succès', 
                        type: 'success' 
                    });
                    // Optionnel : rediriger vers la nouvelle playlist
                    if (data.new_playlist_uuid) {
                        setTimeout(() => {
                            globalThis.location.href = `/playlist/${data.new_playlist_uuid}`;
                        }, 1500);
                    }
                } else if (data.error) {
                    // Gérer les différents types d'erreurs selon le status code
                    let notificationType: 'error' | 'warning' = 'error';
                    
                    if (status === 409) { // Playlist déjà dupliquée
                        notificationType = 'warning';
                    }
                    
                    Notification.createClientNotification({ 
                        message: data.error, 
                        type: notificationType 
                    });
                } else {
                    Notification.createClientNotification({ 
                        message: 'Une erreur inattendue est survenue', 
                        type: 'error' 
                    });
                }
            })
            .catch(error => {
                console.error('Error duplicating playlist:', error);
                Notification.createClientNotification({ 
                    message: 'Erreur de communication avec le serveur', 
                    type: 'error' 
                });
            });
    }
}

