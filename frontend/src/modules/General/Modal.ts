import { Modal } from 'bootstrap';

type ModalJson = {
    title: string;
    body: string;
    footer: string;
    width: string;
    callback?: () => void
}

class ModalCustom {
    public static getMainHTMLElement(): HTMLDivElement {
        return document.getElementById('mainModal')! as HTMLDivElement
    }


    public static show(param: ModalJson = {
        title: "",
        body: "",
        footer: "",
        width: ""
    }) {
        const defaultValues = {
            title: "",
            body: "",
            footer: "",
            width: ""
        }
        const config = { ...defaultValues, ...param };
        const mainModalElement = ModalCustom.getMainHTMLElement();

        const mainModal = new Modal(mainModalElement, {
            keyboard: false
        });

        mainModalElement.classList.remove('modal-lg');
        mainModalElement.classList.remove('modal-sm');
        mainModalElement.classList.remove('modal-xl');
        let width = null
        switch (config.width) {
            case 'lg':
                width = 'modal-lg';
                break;
            case 'sm':
                width = 'modal-sm';
                break;
            case 'xl':
                width = 'modal-xl';
                break;
        }

        if (width) {
            mainModalElement.classList.add(width);
        }

        document.getElementById("mainModalTitle")!.innerHTML = config.title;
        document.getElementById("mainModalBody")!.innerHTML = config.body;
        document.getElementById("mainModalFooter")!.innerHTML = config.footer;


        mainModal.show();
        if (typeof config.callback === 'function') {
            config.callback();
        }
    }

    static hide() {
        const myModalEl = ModalCustom.getMainHTMLElement();
        let modal = Modal.getInstance(myModalEl)
        modal.hide();

        document.getElementById("mainModalTitle")!.innerHTML = "";
        document.getElementById("mainModalBody")!.innerHTML = "";
        document.getElementById("mainModalFooter")!.innerHTML = "";
    }

}

export default ModalCustom;

