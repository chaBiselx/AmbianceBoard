import ModalCustom from '@/modules/General/Modal';
import Csrf from "@/modules/General/Csrf";
import AddMusicModalHandler from "@/modules/SoundBoardEditor/AddMusicModalHandler";



/**
 * Manages the display of the popup for adding music to a soundboard.
 */
class PopupAddMusicToSoundboard {

    url: string;

    /**
     * Creates a new popup manager instance.
     * Can be called with or without parameters for backward compatibility.
     */
    constructor(url: string) {
        this.url = url;
    }

    /**
     * Displays the popup if the necessary values are present.
     * @returns {void}
     */
    public showIfValue(): void {
        fetch(this.url, {
            method: 'GET',
            headers: {
                'X-CSRFToken': Csrf.getToken()!
            }
        }).then(response => response.text()).then((body) => {
            ModalCustom.show({
                title: "Playlist ajoutée",
                body: body,
                footer: "",
                width: "md",
                callback: () => {
                    const handler = new AddMusicModalHandler();
                    handler.initialize();
                }
            });
        });
    }

}

export default PopupAddMusicToSoundboard;

