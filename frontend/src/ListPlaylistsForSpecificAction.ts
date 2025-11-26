import PageFocusReloader from "@/modules/General/PageFocusReloader";
import Csrf from '@/modules/General/Csrf';
import ConsoleCustom from "@/modules/General/ConsoleCustom";
import ShorcutKeyBoardDetector from "@/modules/Control/ShorcutKeyBoardDetector";
import UserConfig from "@/modules/Util/UserConfig";
import Notification from '@/modules/General/Notifications';

document.addEventListener("DOMContentLoaded", () => {
    new PageFocusReloader().setupFocusListener();
    new UpdatePlaylistActionableByPlayers().initEventListeners();
    new UpdatePlaylistShortcutKeyboard().initEventListeners();
    new KeyboardColumnVisibility().toggleColumnVisibility();
});

type valueType = string | boolean | number;

type ActionnableByUserDTO = {
    soundboard_uuid: string;
    playlist_uuid: string;
    soundboard_playlist_id: string;
    label: string;
    value: valueType;
}
type ShortcutKeyboardDTO = {
    soundboard_uuid: string;
    playlist_uuid: string;
    soundboard_playlist_id: string;
    shortcuts: string[] | null;
}

class UpdatePlaylistActionableByPlayers {
    private readonly playlistsTableBody: HTMLElement;
    private readonly url: string;
    constructor() {
        this.playlistsTableBody = document.getElementById('playlists-table-body') as HTMLElement;
        this.url = document.getElementById('col-actionnable-by-players')!.dataset.actionnableByPlayersUrl as string;
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
                const param: ActionnableByUserDTO = {
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

    private updateValueAction(param: ActionnableByUserDTO) {
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
        const hasKeyboard = UserConfig.detectKeyboard();

        if (!hasKeyboard) {
            // Masquer toutes les cellules de la colonne raccourci clavier
            const keyboardCells = document.querySelectorAll('.keyboard-shortcut-column');
            keyboardCells.forEach(cell => {
                (cell as HTMLElement).style.display = 'none';
            });
        }
    }
}

class UpdatePlaylistShortcutKeyboard {
    private readonly playlistsTableBody: HTMLElement;
    // private readonly url: string;
    private readonly shortcutDetector: ShorcutKeyBoardDetector;
    private readonly url: string;
    private readonly classInput: string = 'keyboard-shortcut-event';

    constructor() {
        this.playlistsTableBody = document.getElementById('playlists-table-body') as HTMLElement;
        this.shortcutDetector = new ShorcutKeyBoardDetector();
        this.url = document.getElementById('col-keyboard-shortcut')!.dataset.shortcutUrl as string;
    }

    public initEventListeners(): void {
        for (const input of this.playlistsTableBody.getElementsByClassName(this.classInput)) {
            input.addEventListener('click', (event) => { this.activeDetectionForPlaylist(event); });
        }
    }

    private activeDetectionForPlaylist(event: Event): void {
        const target = event.target as HTMLElement;

        if (target) {
            // Changer le texte pour indiquer l'attente du raccourci
            target.innerHTML = "<small>Réaliser votre raccourci clavier <br/> echap pour annuler - supprimer pour enlever</small>";

            try {
                this.shortcutDetector.startListening(
                    (shortcut) => {
                        const shortcutString = shortcut.join(' + ');
                        const listInput = this.playlistsTableBody.getElementsByClassName(this.classInput) as HTMLCollectionOf<HTMLElement>;
                        let uniqueInput = false;
                        for (const input of listInput) {
                            if (input) {
                                if (input.dataset.valueDefault == shortcutString) {
                                    Notification.createClientNotification({ message: `Le raccourci clavier ${shortcutString} existe déjà : ${input.dataset.name}`, type: 'info' });
                                    this.reinit(target, true);
                                    uniqueInput = true;
                                    break;
                                }
                            }
                        }
                        if (!uniqueInput) {
                            this.applyShortcutToPlaylist(target, shortcut);
                        }
                        this.shortcutDetector.stopListening();
                    },
                    (cancel: boolean) => {
                        // Restaurer le texte original si l'écoute est arrêtée
                        this.reinit(target, cancel);
                        this.shortcutDetector.stopListening();
                    });
            } catch (error) {
                this.reinit(target, false);
                console.error('Erreur lors de la détection du raccourci clavier:', error);
            }

        }
    }

    private applyShortcutToPlaylist(HTMLElement: HTMLElement, shortcut: string[]) {
        HTMLElement.textContent = shortcut.join(' + ');
        HTMLElement.dataset.valueDefault = HTMLElement.textContent;
        this.saveData(HTMLElement, shortcut);
    }

    private reinit(HTMLElement: HTMLElement, Escape: boolean) {
        if (Escape) {
            HTMLElement.textContent = HTMLElement.dataset.valueDefault || "-";
        } else {
            HTMLElement.textContent = "-";
            this.saveData(HTMLElement, null);
        }
    }

    private saveData(HTMLElement: HTMLElement, shortcut: string[] | null) {
        console.log("Saving shortcut data:", shortcut);

        const playlistUuid = HTMLElement.dataset.playlistUuid;
        const soundboard_uuid = HTMLElement.dataset.soundboardUuid;
        const soundboardPlaylistId = HTMLElement.dataset.soundboardPlaylistId;
        if (playlistUuid && soundboardPlaylistId && soundboard_uuid) {
            const param: ShortcutKeyboardDTO = {
                soundboard_uuid: soundboard_uuid,
                playlist_uuid: playlistUuid,
                soundboard_playlist_id: soundboardPlaylistId,
                shortcuts: shortcut
            };
            this.fetchUpdateShortcut(param);
        }
    }

    private fetchUpdateShortcut(param: ShortcutKeyboardDTO) {

        fetch(this.url, {
            method: 'UPDATE',
            headers: {
                'X-CSRFToken': Csrf.getToken()!,
            },
            body: JSON.stringify(param)
        })
            .then(_ => {

            })
            .catch(_ => {
                Notification.createClientNotification({ message: 'Une erreur est survenue', type: 'error' })
            });
    }
}

