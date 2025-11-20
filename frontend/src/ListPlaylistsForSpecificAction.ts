import PageFocusReloader from "@/modules/General/PageFocusReloader";
import Csrf from '@/modules/General/Csrf';
import ConsoleCustom from "@/modules/General/ConsoleCustom";
import ShorcutKeyBoardDetector from "@/modules/Control/ShorcutKeyBoardDetector";

document.addEventListener("DOMContentLoaded", () => {
    new PageFocusReloader().setupFocusListener();
    new UpdatePlaylistActionableByPlayers().initEventListeners();
    new UpdatePlaylistShortcutKeyboard().initEventListeners();
    new KeyboardColumnVisibility().toggleColumnVisibility();
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

class KeyboardColumnVisibility {
    public toggleColumnVisibility(): void {
        // Détecter si un clavier physique est disponible
        const hasKeyboard = this.detectKeyboard();

        if (!hasKeyboard) {
            // Masquer toutes les cellules de la colonne raccourci clavier
            const keyboardCells = document.querySelectorAll('.keyboard-shortcut-column');
            keyboardCells.forEach(cell => {
                (cell as HTMLElement).style.display = 'none';
            });
        }
    }

    private detectKeyboard(): boolean {
        // Vérifier si l'appareil a un clavier physique
        // Les appareils tactiles purs n'ont généralement pas de clavier physique

        // Vérifier si c'est un appareil tactile
        const isTouchDevice = ('ontouchstart' in window) || (navigator.maxTouchPoints > 0);

        // Vérifier le type de pointeur principal
        const hasCoarsePointer = window.matchMedia('(pointer: coarse)').matches;

        // Si c'est un appareil tactile avec pointeur grossier, probablement sans clavier
        if (isTouchDevice && hasCoarsePointer) {
            return false;
        }

        // Par défaut, on considère qu'un clavier est disponible
        return true;
    }
}

class UpdatePlaylistShortcutKeyboard {
    private readonly playlistsTableBody: HTMLElement;
    // private readonly url: string;
    private shortcutDetector: ShorcutKeyBoardDetector;

    constructor() {
        this.playlistsTableBody = document.getElementById('playlists-table-body') as HTMLElement;
        this.shortcutDetector = new ShorcutKeyBoardDetector();
    }

    public initEventListeners(): void {
        for (const input of this.playlistsTableBody.getElementsByClassName('keyboard-shortcut-event')) {
            input.addEventListener('click', (event) => { this.activeDetectionForPlaylist(event); });
        }
    }

    private activeDetectionForPlaylist(event: Event): void {
        const target = event.target as HTMLElement;

        if (target) {
            // Sauvegarder le texte original
            const originalText = target.textContent || target.innerText;

            // Changer le texte pour indiquer l'attente du raccourci
            target.textContent = "Réaliser votre raccourci clavier";

            try {
                this.shortcutDetector.startListening(
                    (shortcut) => {
                        console.log('Listening for shortcuts:', shortcut);

                        this.applyShortcutToPlaylist(target, shortcut);



                        this.shortcutDetector.stopListening();
                    },
                    () => {
                        // Restaurer le texte original si l'écoute est arrêtée
                        target.textContent = originalText;
                    });
            } catch (error) {
                target.textContent = originalText;
                console.error('Erreur lors de la détection du raccourci clavier:', error);
            }

        }
    }

    private applyShortcutToPlaylist(HTMLElement: HTMLElement, shortcut: string[]) {
        HTMLElement.textContent = shortcut.join(' + ');
        console.log('TODO SAVE '); // TODO sauvegarder la commande coté backend


    }
}

