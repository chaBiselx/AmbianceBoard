import Config from '@/modules/General/Config';
import { MusicElement } from '@/modules/MusicElement';
import { MusicElementFactory } from '@/modules/MusicElementFactory';
import { ButtonPlaylist } from '@/modules/ButtonPlaylist';

/**
 * Classe utilitaire pour rechercher des MusicElement par ButtonPlaylist
 */
class SearchMusicElement {
    /**
     * Recherche tous les MusicElement associés à un ButtonPlaylist donné
     * @param buttonPlaylist Le ButtonPlaylist pour lequel rechercher les éléments musicaux
     * @returns Un tableau de MusicElement trouvés
     */
    static searchByButton(buttonPlaylist: ButtonPlaylist): MusicElement[] {
        const audio = document.getElementsByClassName('playlist-audio-' + buttonPlaylist.idPlaylist) as HTMLCollectionOf<HTMLAudioElement>;
        const listMusic: MusicElement[] = [];
        if (audio.length > 0) {
            for (let audioDom of audio) {
                listMusic.push(MusicElementFactory.fromAudioElement(audioDom));
            }
        }
        return listMusic;
    }
}

/**
 * Classe utilitaire pour lister les MusicElement dans le DOM
 */
class ListingAudioElement {
    /**
     * Récupère tous les MusicElement d'un type spécifique
     * @param type Le type de playlist (music, ambient, sfx, etc.)
     * @returns Un tableau de MusicElement du type spécifié
     */
    static getListingAudioElement(type: string): MusicElement[] {
        const audioElementDiv = document.getElementById(Config.SOUNDBOARD_DIV_ID_PLAYERS) as HTMLElement;
        const audio = audioElementDiv.getElementsByClassName('audio-' + type) as HTMLCollectionOf<HTMLAudioElement>;
        const listingMusicElement: MusicElement[] = []
        for (let audioDom of audio) {
            listingMusicElement.push(MusicElementFactory.fromAudioElement(audioDom));
        };
        return listingMusicElement;
    }

    /**
     * Récupère tous les MusicElement présents dans le DOM
     * @returns Un tableau contenant tous les MusicElement
     */
    static getListAllAudio(): MusicElement[] {
        const audioElementDiv = document.getElementById(Config.SOUNDBOARD_DIV_ID_PLAYERS) as HTMLElement;
        const audio = audioElementDiv.getElementsByTagName('audio');
        const listingMusicElement: MusicElement[] = []
        for (let audioDom of audio) {
            listingMusicElement.push(MusicElementFactory.fromAudioElement(audioDom));
        };
        return listingMusicElement;
    }
}

export { SearchMusicElement, ListingAudioElement };
