import Dropzone from 'dropzone';
import Cookie from '@/modules/Cookie';
import Notification from '@/modules/Notifications';
import ModalCustom from './Modal';

/**
 * Gestionnaire pour l'upload multiple de fichiers musicaux avec Dropzone
 * Permet de gérer l'upload de plusieurs fichiers audio en une fois avec personnalisation des noms
 */
export class MusicDropzoneManager {
    private dropzone: Dropzone | null = null;
    private readonly config: MusicDropzoneConfig;

    constructor(config: MusicDropzoneConfig) {
        // Vérifier que le container existe
        this.config = config;
        this.checkElement(config.containerSelector);


        this.initDropzone();
    }

    private checkElement(selector: string): HTMLElement {
        const element = document.querySelector(selector) as HTMLElement;
        if (!element) {
            throw new Error(`Element with selector "${selector}" not found`);
        }
        return element;
    }

    private initDropzone(): void {
        // Configuration Dropzone
        this.dropzone = new Dropzone(this.config.containerSelector, {
            url: this.config.uploadUrl,
            method: "post",
            paramName: "files",
            acceptedFiles: ".mp3,.wav,.ogg",
            addRemoveLinks: false,
            uploadMultiple: true,
            parallelUploads: 10,
            createImageThumbnails: false,
            headers: {
                "X-CSRFToken": Cookie.get('csrftoken')!
            },
        });
        this.dropzone.on("addedfile", (_file: File) => {
            ModalCustom.hide();
        });
        this.dropzone.on("success", (_files: FileList, response: UploadResponse) => {
            this.handleUploadSuccess(_files, response);
        });
        this.dropzone.on("error", (_file: FileList, errorMessage: ErrorResponse) => {
            this.handleUploadError(_file, errorMessage);
        });
    }

    private handleUploadSuccess(_files: FileList, response: UploadResponse): void {
        console.log('Upload response:', response);

        if (response.errors && response.errors.length > 0) {
            console.warn('Upload errors:', response.errors);
        }
        this.showErrors(response.errors || []);
     
        setTimeout(() => {
            window.location.reload();
        }, 500);
    }

    private handleUploadError(_file: FileList, errorMessage: ErrorResponse): void {
        console.error('Upload error:', errorMessage);
        this.showErrors(errorMessage.errors || []);
    }

    private showErrors(errors: Array<string>): void {
        errors.forEach((error: string) => {
            Notification.createClientNotification({ message: error, type: 'danger' });
        });
    }
}

/**
 * Interfaces TypeScript
 */
export interface MusicDropzoneConfig {
    containerSelector: string;
    uploadUrl: string;
}

export interface UploadResponse {
    success: boolean;
    uploaded_files?: Array<{
        id: number;
        filename: string;
        alternativeName: string;
    }>;
    errors?: string[];
}

export interface ErrorResponse {
    success: boolean;
    errors: string[];
}


/**
 * Factory function pour créer une instance de MusicDropzoneManager
 */
export function createMusicDropzone(config: MusicDropzoneConfig): MusicDropzoneManager {
    return new MusicDropzoneManager(config);
}
