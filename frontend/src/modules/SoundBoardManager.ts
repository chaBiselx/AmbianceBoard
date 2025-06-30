import Config from '@/modules/Config';
import { ButtonPlaylist, ListingButtonPlaylist } from '@/modules/ButtonPlaylist';
import { MusicElement, ListingAudioElement } from '@/modules/MusicElement';
import UpdateVolumeElement from '@/modules/UpdateVolumeElement';


class SoundBoardManager {
    static createPlaylistLink(buttonPlaylist: ButtonPlaylist) {
        if (Config.DEBUG) console.log('createPlaylistLink', buttonPlaylist);

        const musicElement = new MusicElement(buttonPlaylist);
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
                (new MusicElement(audioElement[0] as HTMLAudioElement)).delete();
            }
        }

    }

    static removePlaylist(buttonPlaylist: ButtonPlaylist) {
        const audioElement = document.getElementsByClassName(`playlist-audio-${buttonPlaylist.idPlaylist}`) as HTMLCollectionOf<HTMLAudioElement>;
        while (audioElement.length > 0) { // delete all playlist
            (new MusicElement(audioElement[0])).delete();
        }
    }

    static deleteSameTypePlaylist(ButtonPlaylist: ButtonPlaylist) {
        if (Config.DEBUG) console.log('deleteSameTypePlaylist');
        if (Config.DEBUG) console.log(ButtonPlaylist.singleConcurrentread);
        if (ButtonPlaylist.singleConcurrentread) {
            const listingMusicElement = ListingAudioElement.getListingAudioElement(ButtonPlaylist.playlistType);
            for (let musicElement of listingMusicElement) {
                if (Config.DEBUG) console.log("remove", musicElement);
                musicElement.delete();
            }
            const listingButtonPlaylist = ListingButtonPlaylist.getListingAudioElement(ButtonPlaylist.playlistType);
            for (let buttonPlaylist of listingButtonPlaylist) {
                if (Config.DEBUG) console.log("disactive", buttonPlaylist);
                buttonPlaylist.disactive();
            }
        }
    }

    
    static deleteAllMusicPlaylist() {
        if (Config.DEBUG) console.log('deleteAllPlaylist');
        const listingMusicElement = ListingAudioElement.getListAllAudio();
        for (let musicElement of listingMusicElement) {
            if (Config.DEBUG) console.log("remove", musicElement);
            musicElement.delete();
        }
   
    }




}

export { SoundBoardManager };