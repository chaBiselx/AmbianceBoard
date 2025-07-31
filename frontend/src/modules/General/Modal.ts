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

    public static wait() {
        // Récupérer le template modal-template-wait
        const template = document.getElementById('modal-template-wait') as HTMLTemplateElement;
        if (!template) {
            console.error('Template modal-template-wait not found');
            return;
        }

        ModalCustom.show({
            title: "Chargement en cours",
            body: template.innerHTML,
            footer: "",
            width: "sm",
        });
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

        // Récupérer l'instance existante ou en créer une nouvelle
        let mainModal = Modal.getInstance(mainModalElement);
        if (!mainModal) {
            mainModal = new Modal(mainModalElement, {
                keyboard: false
            });
        }

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

    public static hide() {
        const myModalEl = ModalCustom.getMainHTMLElement();
        let modal = Modal.getInstance(myModalEl)
        if (!modal) {
            return;
        }
        modal.hide();

        // Nettoyer le contenu après la fermeture
        myModalEl.addEventListener('hidden.bs.modal', function cleanupContent() {
            document.getElementById("mainModalTitle")!.innerHTML = "";
            document.getElementById("mainModalBody")!.innerHTML = "";
            document.getElementById("mainModalFooter")!.innerHTML = "";
            // Supprimer l'event listener après utilisation
            myModalEl.removeEventListener('hidden.bs.modal', cleanupContent);
        }, { once: true });
    }

}

export default ModalCustom;

