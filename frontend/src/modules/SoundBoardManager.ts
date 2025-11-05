import ConsoleCustom from '@/modules/General/ConsoleCustom';
import ConsoleTesteur from '@/modules/General/ConsoleTesteur';
import { ButtonPlaylist, ListingButtonPlaylist } from '@/modules/ButtonPlaylist';
import { ListingAudioElement } from '@/modules/MusicElementSearcher';
import { MusicElementFactory } from '@/modules/MusicElementFactory';
import UpdateVolumeElement from '@/modules/UpdateVolumeElement';


class SoundBoardManager {
    static createPlaylistLink(buttonPlaylist: ButtonPlaylist) {
        ConsoleTesteur.log('createPlaylistLink', buttonPlaylist);

        const musicElement = MusicElementFactory.fromButtonPlaylist(buttonPlaylist);
        (new UpdateVolumeElement(musicElement)).update();
        musicElement.addToDOM();
        musicElement.play();
    }

    static addPlaylist(buttonPlaylist: ButtonPlaylist) {
        let audioElement = document.getElementsByClassName(`playlist-audio-${buttonPlaylist.idPlaylist}`);
        if (audioElement.length == 0) {

            SoundBoardManager.deleteSameTypePlaylist(buttonPlaylist);
            SoundBoardManager.createPlaylistLink(buttonPlaylist);

        } else {
            buttonPlaylist.disactive();
            while (audioElement.length > 0) { // delete all playlist
                MusicElementFactory.fromAudioElement(audioElement[0] as HTMLAudioElement).delete();
            }
        }

    }

    static removePlaylist(buttonPlaylist: ButtonPlaylist) {
        const audioElement = document.getElementsByClassName(`playlist-audio-${buttonPlaylist.idPlaylist}`) as HTMLCollectionOf<HTMLAudioElement>;
        while (audioElement.length > 0) { // delete all playlist
            MusicElementFactory.fromAudioElement(audioElement[0]).delete();
        }
    }

    static deleteSameTypePlaylist(ButtonPlaylist: ButtonPlaylist) {
        ConsoleTesteur.log('deleteSameTypePlaylist' , ButtonPlaylist.singleConcurrentread);
        if (ButtonPlaylist.singleConcurrentread) {
            const listingMusicElement = ListingAudioElement.getListingAudioElement(ButtonPlaylist.playlistType);
            for (let musicElement of listingMusicElement) {
                ConsoleCustom.log("remove", musicElement);
                musicElement.delete();
            }
            const listingButtonPlaylist = ListingButtonPlaylist.getListingAudioElement(ButtonPlaylist.playlistType);
            for (let buttonPlaylist of listingButtonPlaylist) {
                ConsoleCustom.log("disactive", buttonPlaylist);
                buttonPlaylist.disactive();
            }
        }
    }

    
    static deleteAllMusicPlaylist() {
        ConsoleCustom.log('deleteAllPlaylist');
        const listingMusicElement = ListingAudioElement.getListAllAudio();
        for (let musicElement of listingMusicElement) {
            ConsoleCustom.log("remove", musicElement);
            musicElement.delete();
        }
   
    }




}

export { SoundBoardManager };