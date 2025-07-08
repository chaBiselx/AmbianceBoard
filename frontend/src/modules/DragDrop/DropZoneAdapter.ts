import Dropzone from 'dropzone';
import {IDropZoneAdapter, IDropAndDropConfig, IDropZoneCallbacks } from '@/modules/DragDrop/DragAndDropInterface'

/**
 * Adaptateur pour Dropzone.js
 */
class DropZoneAdapter implements IDropZoneAdapter {
    private dropzone: Dropzone | null = null;
    private readonly config: IDropAndDropConfig;
    private readonly callbacks: IDropZoneCallbacks;
    private isInitialized: boolean = false;

    constructor(config: IDropAndDropConfig, callbacks: IDropZoneCallbacks = {}) {
        this.config = config;
        this.callbacks = callbacks;
    }

    public initialize(): void {
        if (this.isInitialized) return;

        const container = document.querySelector(this.config.containerSelector);
        if (!container) {
            console.error(`Dropzone container ${this.config.containerSelector} not found.`);
            return;
        }

        const dropzoneConfig: Dropzone.DropzoneOptions = {
            url: this.config.uploadUrl,
            method: this.config.method || "post",
            paramName: this.config.paramName || "file",
            acceptedFiles: this.config.acceptedFiles,
            uploadMultiple: this.config.uploadMultiple || false,
            parallelUploads: this.config.parallelUploads || 1,
            createImageThumbnails: this.config.createImageThumbnails,
            addRemoveLinks: this.config.addRemoveLinks,
            headers: this.config.headers || {},
        };

        this.dropzone = new Dropzone(this.config.containerSelector, dropzoneConfig);
        this.attachEventListeners();
        this.isInitialized = true;
    }

    private attachEventListeners(): void {
        if (!this.dropzone) return;

        this.dropzone.on("addedfile", (file: File) => {
            this.callbacks.onFileAdded?.(file);
        });

        // Dropzone utilise des événements différents pour les uploads multiples
        if (this.config.uploadMultiple) {
            this.dropzone.on("successmultiple", (files: File[], response: any) => {
                this.callbacks.onUploadSuccess?.(files, response);
            });
            this.dropzone.on("errormultiple", (files: File[], error: any) => {
                this.callbacks.onUploadError?.(files, error);
            });
        } else {
            this.dropzone.on("success", (file: File, response: any) => {
                this.callbacks.onUploadSuccess?.(file, response);
            });
            this.dropzone.on("error", (file: File, error: any) => {
                this.callbacks.onUploadError?.(file, error);
            });
        }
    }

    public destroy(): void {
        if (this.dropzone) {
            this.dropzone.destroy();
            this.dropzone = null;
            this.isInitialized = false;
        }
    }
}

export default DropZoneAdapter;
