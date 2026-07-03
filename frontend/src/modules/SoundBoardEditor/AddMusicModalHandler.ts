import Notification from '@/modules/General/Notifications';
import Csrf from "@/modules/General/Csrf";
import ConsoleCustom from "@/modules/General/ConsoleCustom";
import { MusicDropzoneConfig, MusicDropzoneManager } from '@/modules/MusicDropzoneManager';
import ModalCustom from '@/modules/General/Modal';


/**
 * Handles modal interactions for adding music to the soundboard.
 */
class AddMusicModalHandler {
    /**
     * Sets up the music dropzone for file uploads.
     * @returns {void}
     */
    private initializeDropzone(): void {
        const dropZone = document.getElementById('music-dropzone');
        if (!dropZone) return;

        const uploadUrl = dropZone.dataset.uploadUrl;
        const csrf = Csrf.getToken();

        if (!uploadUrl) {
            ConsoleCustom.error('Missing required configuration for MusicDropzoneManager');
            return;
        }

        try {
            (globalThis as typeof globalThis & { musicDropzoneManager?: MusicDropzoneManager }).musicDropzoneManager = new MusicDropzoneManager(
                {
                    containerSelector: '#music-dropzone',
                    uploadUrl: uploadUrl,
                    csrf: csrf,
                    fileFormat: dropZone.dataset.format,
                    nbfile: Number.parseInt(dropZone.dataset.musicremaining!),
                    refreshAfterUpload: false,
                } as MusicDropzoneConfig);
        } catch (error) {
            ConsoleCustom.error('Error initializing MusicDropzoneManager:', error);
        }
    }

    /**
     * Configures navigation between different sections of the add music modal.
     * @returns {void}
     */
    private setupSectionNavigation(): void {
        const sectionAction = document.getElementById('selection-type-ajout');
        const sectionAddFile = document.getElementById('form-add-music-from-soundboard');
        const sectionAddLink = document.getElementById('form-add-link-from-soundboard');

        if (!sectionAction || !sectionAddFile || !sectionAddLink) return;

        this.setupAddMusicFileButton(sectionAction, sectionAddFile);
        this.setupAddMusicLinkButton(sectionAction, sectionAddLink);
        this.setupLinkSubmitForm();
    }

    /**
     * Configures the button that allows users to add music from a file.
     * @param {HTMLElement} sectionAction - The action selection section element
     * @param {HTMLElement} sectionAddFile - The file upload section element
     * @returns {void}
     */
    private setupAddMusicFileButton(sectionAction: HTMLElement, sectionAddFile: HTMLElement): void {
        const addMusicFile = document.getElementById('btn-add-music-from-soundboard');
        if (addMusicFile) {
            addMusicFile.addEventListener('click', () => {
                sectionAction.classList.add('d-none');
                sectionAddFile.classList.remove('d-none');
            });
        }
    }

    /**
     * Configures the button that allows users to add music from a link.
     * @param {HTMLElement} sectionAction - The action selection section element
     * @param {HTMLElement} sectionAddLink - The link input section element
     * @returns {void}
     */
    private setupAddMusicLinkButton(sectionAction: HTMLElement, sectionAddLink: HTMLElement): void {
        const addMusicLink = document.getElementById('btn-add-link-from-soundboard');
        if (addMusicLink) {
            addMusicLink.addEventListener('click', () => {
                sectionAction.classList.add('d-none');
                sectionAddLink.classList.remove('d-none');
            });
        }
    }

    /**
     * Configures the form submission behavior for adding music via link.
     * @returns {void}
     */
    private setupLinkSubmitForm(): void {
        const form = document.getElementById('form-add-link-music-ajax');
        const submitBtn = document.getElementById('submit-add-link-ajax') as HTMLButtonElement | null;

        if (!submitBtn || !(form instanceof HTMLFormElement)) return;

        submitBtn.addEventListener('click', (e) => {
            e.preventDefault();
            this.handleLinkSubmit(form);
        });
    }

    /**
     * Processes the link submission request and displays the result to the user.
     * @param {HTMLFormElement} form - The form element containing the music link
     * @returns {void}
     */
    private handleLinkSubmit(form: HTMLFormElement): void {
        const formData = new FormData(form);
        const url = form.action;
        const submitBtn = form.querySelector('button[type="submit"]');

        // Désactiver le bouton pendant l'envoi
        if (submitBtn instanceof HTMLButtonElement) {
            submitBtn.disabled = true;
            submitBtn.textContent = 'Envoi en cours...';
        }

        fetch(url, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    Notification.createClientNotification({ message: data.message, type: 'success' });
                    const bsModal = ModalCustom.getInstance();
                    if (bsModal) bsModal.hide();
                } else {
                    Notification.createClientNotification({ message: 'Une erreur est survenue', type: 'error' });
                }
            })
            .catch(_ => {
                Notification.createClientNotification({ message: 'Une erreur est survenue', type: 'error' });
            })
            .finally(() => {
                if (submitBtn instanceof HTMLButtonElement) {
                    submitBtn.disabled = false;
                    submitBtn.textContent = 'Envoyer';
                }
            });
    }

    /**
     * Initializes all components of the add music modal.
     * @returns {void}
     */
    public initialize(): void {
        this.initializeDropzone();
        this.setupSectionNavigation();
    }
}

export default AddMusicModalHandler;