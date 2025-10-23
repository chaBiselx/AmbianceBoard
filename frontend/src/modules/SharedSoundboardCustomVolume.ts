import ModalCustom from '@/modules/General/Modal';
import Cookie from "@/modules/General/Cookie";
import { SearchMusicElement } from "@/modules/MusicElement";
import { ButtonPlaylistFinder } from "@/modules/ButtonPlaylist";
import UpdateVolumeElement from '@/modules/UpdateVolumeElement';

class SharedSoundboardCustomVolumeFactory {
    static create(idButton: string, idElement: string): SharedSoundboardCustomVolume | null {
        const DOMTemplate = document.getElementById(idElement);
        const DOMButton = document.getElementById(idButton);
        if (DOMTemplate?.dataset?.sharedVolumeSoundboardId && DOMButton && DOMButton instanceof HTMLButtonElement) {
            return new SharedSoundboardCustomVolume(DOMTemplate, DOMButton);
        }
        return null;
    }
}

class SharedSoundboardIdFinder {
    static findSoundBoardId(id: string): string | null {
        const element = document.getElementById(id);
        return element?.dataset?.sharedVolumeSoundboardId || null;
    }
}

class SharedSoundboardCustomVolume {
    DOMTemplate: HTMLElement;
    DOMButton: HTMLButtonElement;
    cookieName: string;
    jsonValue: Record<string, number>;
    minValue: number = 10;

    constructor(DOMTemplate: HTMLElement, DOMButton: HTMLButtonElement) {
        this.DOMTemplate = DOMTemplate;
        this.DOMButton = DOMButton;
        this.cookieName = `SharedPlaylistCustomVolume_${DOMTemplate.dataset.sharedVolumeSoundboardId!}`;

        const dataCookie = Cookie.get(this.cookieName);
        this.jsonValue = dataCookie ? JSON.parse(dataCookie) : {};
    }

    public addEvent() {
        this.DOMButton.addEventListener('click', this.getElementsToUpdateVolume.bind(this));
    }

    private getElementsToUpdateVolume() {
        const body = this.processCopyPastReportable();
        this.showModal("Reporting content", body)
    }

    private processCopyPastReportable(): string {
        let divGeneral = document.createElement('div');

        let sectionSelectElement = document.createElement('section');
        sectionSelectElement.classList.add("responsive-sections-container");
        sectionSelectElement.appendChild(this.generateSelector());
        divGeneral.appendChild(sectionSelectElement);



        return divGeneral.outerHTML
    }

    private generateSelector(): HTMLElement {
        let selectElement = document.createElement('div');
        selectElement.classList.add('flex-container');


        const reportableElements = this.DOMTemplate.querySelectorAll('.playlist-link')
        for (const element of reportableElements) {
            let flexItem = document.createElement('div');
            flexItem.classList.add('flex-item');
            let clonedElement = element.cloneNode(true) as HTMLElement;
            for (const el of clonedElement.children) {
                if (!(el instanceof HTMLImageElement)) {
                    el.remove();
                }
            }
            const value = this.jsonValue[`${clonedElement.dataset.playlistId}`] ? this.jsonValue[`${clonedElement.dataset.playlistId}`] : 100;

            const html = `<form class="mixer-playlist-update-container">
            <input class="mixer-playlist-custom-shared-update horizontal-slider-input" type="range" value="${value}" min="${this.minValue}" max="100" id="range__custom_volume_${clonedElement.dataset.playlistId}" 
            data-idplaylist="${clonedElement.dataset.playlistId}" style="width: 75px;" />
            <output class="horizontal-slider-output bottom" for="range__custom_volume_${clonedElement.dataset.playlistId}" style="--min: ${value};--max: 100"></output>
            </form>`;
            const tempDiv = document.createElement('div');
            tempDiv.innerHTML = html;
            flexItem.appendChild(clonedElement);
            flexItem.appendChild(tempDiv.firstElementChild as Node);
            selectElement.appendChild(flexItem);
        };
        return selectElement

    }

    private showModal(title: string, body: string) {
        ModalCustom.show({
            title: title,
            body: body,
            footer: "",
            width: "xl",
            callback: () => {
                const reportableElements = document.querySelectorAll('.mixer-playlist-custom-shared-update')
                for (const element of reportableElements) {
                    element.addEventListener('change',
                        (event: Event) => {
                            this.handleChangeForm(event)
                        }
                    )
                }
            }
        })

    }

    private handleChangeForm(event: Event) {
        event.preventDefault();
        const elementClicked = event.target as HTMLInputElement;
        if (elementClicked.dataset.idplaylist) {
            try {
                this.setCookie(
                    elementClicked.dataset.idplaylist,
                    Number.parseInt(elementClicked.value)
                );
            } catch (error) {
                console.error(error);
            }

            this.updateVolumeElements(elementClicked.dataset.idplaylist!);
        }
    }

    private updateVolumeElements(idPlaylist: string): this {
        const button = ButtonPlaylistFinder.search(idPlaylist);
        if (button) {
            const listMusic = SearchMusicElement.searchByButton(button);
            for (const musicElement of listMusic) {
                new UpdateVolumeElement(musicElement).update();
            }
        }
        return this
    }

    private setCookie(id: string, value: number) {
        this.jsonValue[`${id}`] = value;
        Cookie.set(this.cookieName, JSON.stringify(this.jsonValue));
    }
}


export { SharedSoundboardCustomVolumeFactory, SharedSoundboardIdFinder };

