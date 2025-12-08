

import { ButtonPlaylist } from '@/modules/ButtonPlaylist';
import { SoundBoardManager } from '@/modules/SoundBoardManager';
import SharedSoundboardSendCmdMaster from '@/modules/SharedSoundboardSendCmdMaster';
import Time from '@/modules/Util/Time';

class SoundBoardEventListener {


    public addEventListenerDom() {
        const formElements = document.querySelectorAll('.playlist-link');
        for (const element of formElements) {
            if (element.classList.contains('disabled')) continue
            if (element.classList.contains('playlist-user-playable')) {
                element.addEventListener('click', (event) => this.eventPlayInMasterSoundboard(event));
            } else {
                element.addEventListener('click', (event) => this.eventTogglePlaylist(event));
            }
        }
    }

    private eventTogglePlaylist(event: Event) {
        if (event.target instanceof HTMLElement) {
            const buttonPlaylist = new ButtonPlaylist(event.target)
            if (buttonPlaylist.isActive()) {
                buttonPlaylist.disactive();
                SoundBoardManager.removePlaylist(buttonPlaylist);
            } else {
                buttonPlaylist.active();
                SoundBoardManager.addPlaylist(buttonPlaylist);
            }
        }
    }

    private eventPlayInMasterSoundboard(event: Event) {
        if (event.target instanceof HTMLElement) {
            const buttonPlaylist = new ButtonPlaylist(event.target)
            if (!buttonPlaylist.isActive()) {
                new SharedSoundboardSendCmdMaster().sendPlayPlaylistOnMaster(buttonPlaylist.getUuid());
                buttonPlaylist.active();
                setTimeout(() => {
                    buttonPlaylist.disactive();
                }, Time.get_seconds(1));
            }
        }
    }

}
export default SoundBoardEventListener;