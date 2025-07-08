import Notification from '@/modules/Notifications';
import ModalCustom from './Modal';
import {
    IDropAndDropConfig,
    IDropZoneAdapter,
    IDropZoneCallbacks,
    IUploadResponse
} from '@/modules/DragDrop/DragAndDropInterface';
import DropZoneAdapter from '@/modules/DragDrop/DropZoneAdapter'

/**
 * Gestionnaire pour l'upload multiple de fichiers musicaux avec Dropzone
 * Utilise l'abstraction DropZoneAdapter pour une meilleure maintenabilité
 */
export class MusicDropzoneManager {
    private dropzoneAdapter: IDropZoneAdapter | null = null;
    private readonly config: MusicDropzoneConfig;

    constructor(config: MusicDropzoneConfig) {
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
        const callbacks: IDropZoneCallbacks = {
            onFileAdded: (_file: File) => {
                ModalCustom.hide();
            },
            onUploadSuccess: (files: File | File[] | FileList, response: IUploadResponse) => {
                this.handleUploadSuccess(files, response);
            },
            onUploadError: (files: File | File[] | FileList, error: any) => {
                this.handleUploadError(files, error);
            }
        };
        const dragAndDropConfig = {
            containerSelector: this.config.containerSelector,
            uploadUrl: this.config.uploadUrl,
            acceptedFiles: ".mp3,.wav,.ogg",
            uploadMultiple: true,
            parallelUploads: 5,
            createImageThumbnails: false,
            addRemoveLinks: false,
            headers: {
                "X-CSRFToken": this.config.csrf
            },
            paramName: "files",
            method: "post",


        } as IDropAndDropConfig;

        this.dropzoneAdapter = new DropZoneAdapter(dragAndDropConfig, callbacks);

        this.dropzoneAdapter?.initialize();
    }

    private handleUploadSuccess(_files: File | File[] | FileList, response: IUploadResponse): void {
        console.log('Upload response:', response);

        if (response.errors && response.errors.length > 0) {
            console.warn('Upload errors:', response.errors);
        }
        this.showErrors(response.errors || []);

        setTimeout(() => {
            window.location.reload();
        }, 500);
    }

    private handleUploadError(_files: File | File[] | FileList, errorMessage: any): void {
        console.error('Upload error:', errorMessage);
        const errors = errorMessage.errors || (typeof errorMessage === 'string' ? [errorMessage] : ['An unknown error occurred']);
        this.showErrors(errors);
    }

    private showErrors(errors: Array<string>): void {
        errors.forEach((error: string) => {
            Notification.createClientNotification({ message: error, type: 'danger' });
        });
    }

    public destroy(): void {
        this.dropzoneAdapter?.destroy();
    }
}

/**
 * Interfaces TypeScript
 */
export interface MusicDropzoneConfig {
    containerSelector: string;
    uploadUrl: string;
    csrf : string;
}

/**
 * Factory function pour créer une instance de MusicDropzoneManager
 */
export function createMusicDropzone(config: MusicDropzoneConfig): MusicDropzoneManager {
    return new MusicDropzoneManager(config);
}
